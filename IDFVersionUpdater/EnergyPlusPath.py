import glob
import os
from .TransitionBinary import TransitionBinary


class EnergyPlusPath(object):
    """
    This class provides a summary of the latest installed version of EnergyPlus
    The constructor looks up the available installations, picks the most recent (inferred from version number),
    and sets some parameters

    :ivar installation_path: An installation path on Mac, following the form: '/Applications/EnergyPlus-?-?-?/'
    :ivar version_number: The version number suffix, in the form: '?-?-?'
    :ivar transition_directory: Absolute path to a transition run directory within the given installation directory
    :ivar transitions_available: A list of :py:class:`TransitionBinary <TransitionBinary.TransitionBinary>`
        instances available in this installation
    """

    def __init__(self):
        # get all the installed versions first, and sort them, then return the last one
        cur_platform = self.get_platform()
        install_folders = []
        if cur_platform == "linux":
            install_folders = glob.glob('/usr/local/EnergyPlus*')
        elif cur_platform == "mac":
            install_folders = glob.glob('/Applications/EnergyPlus*')
        elif cur_platform == "windows":
            install_folders = glob.glob('C:/EnergyPlusV*')
        ep_versions = sorted([x for x in install_folders])
        self.installation_path = ep_versions[-1]
        self.version_number = self.get_version_number()
        self.transition_directory = self.get_transition_run_dir()
        self.transitions_available = self.get_transitions_available()

    # TODO: Move this to a standalone path class, change to enums
    @staticmethod
    def get_platform():
        from sys import platform as _platform
        if _platform.startswith("linux"):
            return "linux"
        elif _platform == "darwin":
            return "mac"
        elif _platform.startswith("win32"):
            return "windows"

    def get_version_number(self):
        """
        This function processes the found installation path, and returns just the version number portion.
        This is basically the inverse of :py:meth:`EnergyPlusPath.get_path_from_version_number`

        :rtype: The version number suffix, in the form: '?-?-?'
        """
        ep_folder = self.installation_path.split(os.sep)[-1]
        if 'EnergyPlus' not in ep_folder:
            return None
        return ep_folder[11:]

    def get_transition_run_dir(self):
        """
        This function returns the full path to a transition folder in the found installation path

        :rtype: Absolute path to a transition run directory within the given installation directory
        """
        return os.path.join(self.installation_path, 'PreProcess', 'IDFVersionUpdater')

    def get_transitions_available(self):
        """
        This function returns a list of transition instances available in a given transition run directory

        :rtype: A list of :py:class:`TransitionBinary <TransitionBinary.TransitionBinary>` instances
            available in this installation
        """
        binary_paths = glob.glob(os.path.join(self.transition_directory, 'Transition-V*'))
        return [TransitionBinary(x) for x in binary_paths]
