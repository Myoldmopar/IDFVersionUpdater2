import os
import sys
import unittest

# add the source directory to the path so the unit test framework can find it
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'IDFVersionUpdater'))

from TransitionBinary import TransitionBinary


class TestTransitionBinary(unittest.TestCase):
    def test_good_transition_object(self):
        valid_path = "/Applications/EnergyPlus-8-5-0/PreProcess/IDFVersionUpdater/Transition-V8-5-0-to-V8-6-0"
        valid_object = TransitionBinary(valid_path)
        self.assertEqual(valid_object.full_path_to_binary, valid_path)
        self.assertEqual(valid_object.binary_name, "Transition-V8-5-0-to-V8-6-0")
        self.assertEqual(valid_object.source_version, 8.5)
        self.assertEqual(valid_object.target_version, 8.6)

    def test_transition_object_just_file_name(self):
        just_file_name = "Transition-V8-5-0-to-V8-6-0"
        just_file_name_object = TransitionBinary(just_file_name)
        self.assertEqual(just_file_name_object.full_path_to_binary, just_file_name)
        self.assertEqual(just_file_name_object.binary_name, "Transition-V8-5-0-to-V8-6-0")
        self.assertEqual(just_file_name_object.source_version, 8.5)
        self.assertEqual(just_file_name_object.target_version, 8.6)

    def test_bad_transition_object(self):
        invalid_path = "/Applications/EnergyPlus-8-5-0/PreProcess/IDFVersionUpdater/BadBinaryName"
        with self.assertRaises(Exception):
            TransitionBinary(invalid_path)
