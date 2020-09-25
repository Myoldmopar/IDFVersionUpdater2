import os
import shutil
import subprocess
import threading

from .International import translate as _


class TransitionRunThread(threading.Thread):
    """
    This class allows easily running a series of EnergyPlus Transition program versions in a separate thread

    :param transitions_to_run: A list of :py:class:`TransitionBinary <TransitionBinary.TransitionBinary>` instances to be run
    :param working_directory: The transition working directory to run transitions in
    :param original_file_path: The absolute file path to the file to be transitioned
    :param keep_old: A boolean flag for whether to keep an extra backup of the original file to be transitioned in the run folder
    :param msg_callback: A Python function to be called back by this thread when a message can be displayed
    :param done_callback: A Python function to be called back by this thread when the transition process is complete

    :ivar std_out: The standard output from the transition process
    :ivar std_err: The standard error output from the transition process
    """

    def __init__(self, transitions_to_run, working_directory, original_file_path, keep_old, msg_callback, done_callback):
        self.p = None
        self.std_out = None
        self.std_err = None
        self.transitions = transitions_to_run
        self.run_dir = working_directory
        self.input_file = original_file_path
        self.keep_old = keep_old
        self.msg_callback = msg_callback
        self.done_callback = done_callback
        self.cancelled = False
        threading.Thread.__init__(self)

    def backup_file_before_transition(self, transition_instance):
        input_file_name = os.path.basename(self.input_file)
        source_file_path = os.path.join(self.run_dir, input_file_name)
        input_file_name_parts = os.path.splitext(input_file_name)
        target_backup_file_name = input_file_name_parts[0] + "_" + str(transition_instance.source_version) + input_file_name_parts[1]
        target_backup_file_path = os.path.join(self.run_dir, target_backup_file_name)
        if os.path.exists(target_backup_file_path):
            try:
                os.remove(target_backup_file_path)
            except Exception:
                return False
        try:
            shutil.copyfile(source_file_path, target_backup_file_path)
        except Exception:
            return False
        return True

    def run(self):
        """
        This function runs the instantiated thread based on the parameters passed into the constructor.
        The function intermittently calls the msg_callback class instance function variable to alert the calling thread of status updates.
        When the function is complete it calls the done_callback class instance function variable to alert the calling thread.
        """
        self.cancelled = False
        shutil.copy(self.input_file, self.run_dir)
        base_file_name = os.path.basename(self.input_file)
        failed = False
        cancelled = False
        for tr in self.transitions:
            if self.keep_old:
                backup_success = self.backup_file_before_transition(tr)
                if not backup_success:
                    failed = True
                    break
            command_line_tokens = [
                tr.full_path_to_binary,
                base_file_name,
            ]
            self.p = subprocess.Popen(
                command_line_tokens,
                shell=False,
                cwd=self.run_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            self.msg_callback(_("Running Transition") + " " + str(tr.source_version) + " -> " + str(tr.target_version))
            self.std_out, self.std_err = self.p.communicate()
            if self.cancelled:
                self.msg_callback(_("Transition Cancelled"))
                break
            else:
                if self.p.returncode == 0:
                    self.msg_callback(
                        _("Completed Transition") + " " + str(tr.source_version) + " -> " + str(tr.target_version))
                else:
                    self.msg_callback(
                        _("Failed Transition") + " " + str(tr.source_version) + " -> " + str(tr.target_version))
                    failed = True
                    break
        if self.cancelled:
            self.done_callback(_("Transition cancelled"))
        elif failed:
            self.done_callback(_("Transition Failed! - Open run directory to read latest audit/error/etc"))
        else:
            self.done_callback(_("All transitions completed successfully - Open run directory for transitioned file"))

    @staticmethod
    def get_ep_version(run_script):
        """
        This function returns a human friendly version identifier for a given EnergyPlus binary.
        This function relies on the ``-v`` flag for the EnergyPlus binary

        :param run_script: Absolute path to an EnergyPlus main binary
        :rtype: Returns a human friendly EnergyPlus version identifier; the exact format is not defined
        """
        p = subprocess.Popen([run_script, '-v'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = p.communicate()
        return std_out.strip()

    def stop(self):
        """
        This function allows attempting to stop the thread if it is running.
        This function polls the existing subprocess to see if it is running and attempts to kill the process
        """
        if self.p.poll() is None:
            self.msg_callback(_("Attempting to cancel simulation ..."))
            self.cancelled = True
            self.p.kill()
