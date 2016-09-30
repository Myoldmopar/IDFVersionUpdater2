import os
import shutil
import subprocess
import threading

from International import translate as _


class EnergyPlusThread(threading.Thread):
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

    def run(self):
        self.cancelled = False
        shutil.copy(self.input_file, self.run_dir)
        base_file_name = os.path.basename(self.input_file)
        if self.keep_old:
            shutil.copyfile(self.input_file, os.path.join(self.run_dir, 'before-transition-'+base_file_name))
        for tr in self.transitions:
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
                # self.cancelled_callback()
            else:
                if self.p.returncode == 0:
                    self.msg_callback(
                        _("Completed Transition") + " " + str(tr.source_version) + " -> " + str(tr.target_version))
                    # self.success_callback(self.std_out, self.run_dir)
                else:
                    self.msg_callback(
                        _("Failed Transition") + " " + str(tr.source_version) + " -> " + str(tr.target_version))
                    break
                    # self.failure_callback(self.std_out, self.run_dir, subprocess.list2cmdline(command_line_tokens))
        self.done_callback(_("All transitions completed successfully - Open run directory for transitioned file"))

    @staticmethod
    def get_ep_version(run_script):
        p = subprocess.Popen([run_script, '-v'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = p.communicate()
        return std_out.strip()

    def stop(self):
        if self.p.poll() is None:
            self.msg_callback(_("Attempting to cancel simulation ..."))
            self.cancelled = True
            self.p.kill()
