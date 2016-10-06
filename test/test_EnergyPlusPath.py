import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'IDFVersionUpdater'))

from EnergyPlusPath import EnergyPlusPath


class TestEnergyPlusPaths(unittest.TestCase):
    def test_proper_path_no_trailing_slash(self):
        eight_one = EnergyPlusPath.get_version_number_from_path('/Applications/EnergyPlus-8-1-0')
        self.assertEqual(eight_one, '8-1-0')

    def test_proper_path_with_trailing_slash(self):
        eight_one = EnergyPlusPath.get_version_number_from_path('/Applications/EnergyPlus-8-1-0/')
        self.assertEqual(eight_one, '8-1-0')

    def test_bad_path_with_enough_tokens(self):
        eight_one = EnergyPlusPath.get_version_number_from_path('/usr/local/EnergyPlus-8-1-0')
        self.assertIsNone(eight_one)

    def test_bad_path_not_enough_tokens(self):
        with self.assertRaises(IndexError):
            EnergyPlusPath.get_version_number_from_path('/EnergyPlus-8-1-0')

