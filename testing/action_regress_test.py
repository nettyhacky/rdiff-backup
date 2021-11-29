"""
Test the remove action with api version >= 201
"""
import os
import unittest

import commontest as comtst
import fileset

from rdiff_backup import Globals, rpath, Time
from rdiffbackup.locations import _repo_shadow


class ActionRegressTest(unittest.TestCase):
    """
    Test that rdiff-backup properly does regression
    """

    def setUp(self):
        self.base_dir = os.path.join(comtst.abs_test_dir, b"action_regress")
        self.from1_struct = {
            "from1": {"subs": {
                "fileChanged": {"content": "initial"},
                "fileOld": {},
                "fileUnchanged": {"content": "unchanged"},
            }}
        }
        self.from1_path = os.path.join(self.base_dir, b"from1")
        self.from2_struct = {
            "from2": {"subs": {
                "fileChanged": {"content": "modified"},
                "fileNew": {},
                "fileUnchanged": {"content": "unchanged"},
            }}
        }
        self.from2_path = os.path.join(self.base_dir, b"from2")
        self.from3_struct = {
            "from3": {"subs": {
                "fileChanged": {"content": "modified again"},
                "fileNew": {},
                "fileUnchanged": {"content": "unchanged"},
            }}
        }
        self.from3_path = os.path.join(self.base_dir, b"from3")
        self.from4_struct = {
            "from4": {"subs": {
                "fileChanged": {"content": "modified again"},
                "fileEvenNewer": {},
                "fileUnchanged": {"content": "unchanged"},
            }}
        }
        self.from4_path = os.path.join(self.base_dir, b"from4")
        fileset.create_fileset(self.base_dir, self.from1_struct)
        fileset.create_fileset(self.base_dir, self.from2_struct)
        fileset.create_fileset(self.base_dir, self.from3_struct)
        fileset.create_fileset(self.base_dir, self.from4_struct)
        fileset.remove_fileset(self.base_dir, {"bak": {}})
        self.bak_path = os.path.join(self.base_dir, b"bak")
        self.to2_path = os.path.join(self.base_dir, b"to2")
        self.to4_path = os.path.join(self.base_dir, b"to4")
        # we backup to the same backup repository at different times
        comtst.rdiff_backup_action(
            True, True, self.from1_path, self.bak_path,
            ("--api-version", "201", "--current-time", "10000"),
            b"backup", ())
        comtst.rdiff_backup_action(
            True, True, self.from2_path, self.bak_path,
            ("--api-version", "201", "--current-time", "20000"),
            b"backup", ())
        comtst.rdiff_backup_action(
            True, True, self.from3_path, self.bak_path,
            ("--api-version", "201", "--current-time", "30000"),
            b"backup", ())
        self.success = False

    def test_action_regress(self):
        """test different ways of regressing"""
        # regressing a successful backup doesn't do anything
        self.assertEqual(comtst.rdiff_backup_action(
            False, None, self.bak_path, None,
            ("--api-version", "201"),
            b"regress", ()), 0)
        # we again simulate a crash
        _repo_shadow.ShadowRepo.touch_current_mirror(
            rpath.RPath(Globals.local_connection,
                        self.bak_path, ("rdiff-backup-data",)),
            Time.timetostring(20000))
        # the current process (the test) is still running, hence it fails
        self.assertNotEqual(comtst.rdiff_backup_action(
            True, None, self.bak_path, None,
            ("--api-version", "201"),
            b"regress", ()), 0)
        # but it runs with --force
        self.assertEqual(comtst.rdiff_backup_action(
            True, None, self.bak_path, None,
            ("--api-version", "201", "--force"),
            b"regress", ()), 0)
        # we restore and compare
        self.assertEqual(comtst.rdiff_backup_action(
            True, True, self.bak_path, self.to2_path,
            ("--api-version", "201"),
            b"restore", ()), 0)
        self.assertFalse(fileset.compare_paths(self.from2_path, self.to2_path))
        # we again simulate a crash
        _repo_shadow.ShadowRepo.touch_current_mirror(
            rpath.RPath(Globals.local_connection,
                        self.bak_path, ("rdiff-backup-data",)),
            Time.timetostring(10000))
        # and then try to backup, which fails because without force
        self.assertNotEqual(comtst.rdiff_backup_action(
            True, True, self.from4_path, self.bak_path,
            ("--api-version", "201", "--current-time", "40000"),
            b"backup", ()), 0)
        # now with --force, it can't be exactly the same time or it fails
        # on error_log already existing
        self.assertEqual(comtst.rdiff_backup_action(
            True, True, self.from4_path, self.bak_path,
            ("--api-version", "201", "--current-time", "40001", "--force"),
            b"backup", ()), 0)
        # we restore and compare
        self.assertEqual(comtst.rdiff_backup_action(
            True, True, self.bak_path, self.to4_path,
            ("--api-version", "201"),
            b"restore", ()), 0)
        self.assertFalse(fileset.compare_paths(self.from4_path, self.to4_path))

        # all tests were successful
        self.success = True

    def tearDown(self):
        # we clean-up only if the test was successful
        if self.success:
            fileset.remove_fileset(self.base_dir, self.from1_struct)
            fileset.remove_fileset(self.base_dir, self.from2_struct)
            fileset.remove_fileset(self.base_dir, self.from3_struct)
            fileset.remove_fileset(self.base_dir, self.from4_struct)
            fileset.remove_fileset(self.base_dir, {"bak": {}})
            fileset.remove_fileset(self.base_dir, {"to2": {}})
            fileset.remove_fileset(self.base_dir, {"to4": {}})


if __name__ == "__main__":
    unittest.main()