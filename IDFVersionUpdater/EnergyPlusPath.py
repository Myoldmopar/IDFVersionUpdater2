import glob
import os
# TODO: Clean out unused functions here
# TODO: Really nice to just make this a full class instead of just a collection of static functions
# TODO: Cross platform this whole thing


class TransitionBinary(object):
    """
    This class describes a single transition binary in the installation
    The class is constructed from the full path to the binary, then source and target versions are parsed from this path and the filenames

    :param full_path: Full path to the transition binary itself

    :ivar full_path_to_binary: Copy of the full path to binary passed into the constructor
    :ivar binary_name: This is just the filename portion of the binary executable
    :ivar source_version: This is the source version of this particular transition, for example, in V8-5-0-to-8-6-0, this will be 8.5
    :ivar target_version: This is the target version of this particular transition, for example, in V8-5-0-to-8-6-0, this will be 8.6
    """

    def __init__(self, full_path):
        self.full_path_to_binary = full_path
        self.binary_name = os.path.basename(full_path)
        self.source_version = float(self.binary_name[12:15].replace('-', '.'))
        self.target_version = float(self.binary_name[22:25].replace('-', '.'))


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
        :rtype: A list of :py:class:`TransitionBinary` instances available in this installation
        """
        binary_paths = glob.glob(os.path.join(transition_run_directory, 'Transition-V*'))
        return [TransitionBinary(x) for x in binary_paths]

    @staticmethod
    def get_idf_version(path_to_idf):
        """
        This function returns the current version of a given input file.
        The function uses a simplified parsing approach so it only works for valid syntax files, and provides no specialized error handling

        :param path_to_idf: Absolute path to a EnergyPlus input file
        :rtype: A floating point version number for the input file, for example 8.5 for an 8.5.0 input file
        """
        # phase 1: read in lines of file
        with open(path_to_idf, "r") as fo:
            lines = fo.readlines()
        # phases 2: remove comments and blank lines
        lines_a = []
        for line in lines:
            line_text = line.strip()
            this_line = ""
            if len(line_text) > 0:
                exclamation = line_text.find("!")
                if exclamation == -1:
                    this_line = line_text
                elif exclamation == 0:
                    this_line = ""
                elif exclamation > 0:
                    this_line = line_text[:exclamation]
                if not this_line == "":
                    lines_a.append(this_line)
        # phase 3: join entire array and re-split by semicolon
        idf_data_joined = ''.join(lines_a)
        idf_object_strings = idf_data_joined.split(";")
        # phase 4: break each object into an array of object name and field values
        for this_object in idf_object_strings:
            tokens = this_object.split(',')
            if tokens[0].upper() == "VERSION":
                version_string = tokens[1]
                version_string_tokens = version_string.split('.')  # might be 2 or 3...
                version_number = float("%s.%s" % (version_string_tokens[0], version_string_tokens[1]))
                return version_number
