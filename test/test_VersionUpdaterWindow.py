import os
import sys
import tempfile
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'IDFVersionUpdater'))

from VersionUpdaterWindow import VersionUpdaterWindow


class TestGetIDFVersion(unittest.TestCase):
    def setUp(self):
        self.idf_name = tempfile.mktemp()

    def test_good_version_number(self):
        with open(self.idf_name, 'w') as f:
            f.write("Version,8.5.0;")
        version = VersionUpdaterWindow.get_idf_version(self.idf_name)
        self.assertEqual(version, 8.5)

    def test_bad_version_number(self):
        with open(self.idf_name, 'w') as f:
            f.write("Version,x.y.z;")
        with self.assertRaises(ValueError):
            VersionUpdaterWindow.get_idf_version(self.idf_name)

    def test_missing_version_number(self):
        with open(self.idf_name, 'w') as f:
            f.write("x,y;")
        version = VersionUpdaterWindow.get_idf_version(self.idf_name)
        self.assertIsNone(version)
