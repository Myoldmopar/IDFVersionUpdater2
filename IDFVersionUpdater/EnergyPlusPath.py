import glob
import os
from TransitionBinary import TransitionBinary
# TODO: Really nice to just make this a full class instead of just a collection of static functions
# TODO: Cross platform this whole thing


class EnergyPlusPath(object):
    """
    This class provides static helpers for moving between EnergyPlus install paths and version numbers

    *Note that this class holds no instance data.*
    """

    @staticmethod
    def get_version_number_from_path(path):
        """
        This function takes a Mac EnergyPlus installation path, and returns just the version number portion.
        This is basically the inverse of :py:meth:`EnergyPlusPath.get_path_from_version_number`

        :param path: An installation path on Mac, following the form: '/Applications/EnergyPlus-?-?-?/'
        :rtype: The version number suffix, in the form: '?-?-?'
        """
        # TODO: Cross platform
        ep_folder = path.split('/')[2]
        if 'EnergyPlus' not in ep_folder:
            return None
        return ep_folder[11:]

    @staticmethod
    def get_path_from_version_number(version):
        """
        This function takes a version number, in the standard ?-?-? form and produces a full installation path from it.
        This is basically the inverse of :py:meth:`EnergyPlusPath.get_version_number_from_path`

        :param version: The version number, in the form: '?-?-?'
        :rtype: An installation path on Mac, following the form: '/Applications/EnergyPlus-?-?-?/'
        """
        return '/Applications/EnergyPlus-%s' % version

    @staticmethod
    def get_latest_eplus_version():
        """
        This function searches the default installation path for EnergyPlus, finds all versions, and returns the full path to the newest installation (inferred by version number)

        :rtype: An installation path on Mac, following the form: '/Applications/EnergyPlus-?-?-?/'
        """
        # get all the installed versions first, sorted
        install_folders = glob.glob('/Applications/EnergyPlus*')

        # then process them into a nice list
        ep_versions = sorted([EnergyPlusPath.get_version_number_from_path(x) for x in install_folders])

        # set current_entry to something meaningful if needed
        new_version = ep_versions[-1]
        return EnergyPlusPath.get_path_from_version_number(new_version)

    @staticmethod
    def get_transition_run_dir(eplus_install_directory):
        """
        This function returns the full path to a transition folder in a given installation directory

        :param eplus_install_directory: An EnergyPlus installation directory path
        :rtype: Absolute path to a transition run directory within the given installation directory
        """
        return os.path.join(eplus_install_directory, 'PreProcess', 'IDFVersionUpdater')

    @staticmethod
    def get_transitions_available(transition_run_directory):
        """
        This function returns a list of transition instances available in a given transition run directory

        :param transition_run_directory: A transition directory within a given EnergyPlus installation, as would be returned by :py:meth:`EnergyPlusPath.get_transition_run_dir`
        :rtype: A list of :py:class:`TransitionBinary <TransitionBinary.TransitionBinary>` instances available in this installation
        """
        binary_paths = glob.glob(os.path.join(transition_run_directory, 'Transition-V*'))
        return [TransitionBinary(x) for x in binary_paths]
