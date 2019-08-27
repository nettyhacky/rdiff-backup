import unittest
from commontest import MirrorTest, old_inc1_dir, old_inc2_dir, old_inc3_dir, old_inc4_dir
from rdiff_backup import Globals, SetConnections, user_group, log


class RemoteMirrorTest(unittest.TestCase):
    """Test mirroring"""

    def setUp(self):
        """Start server"""
        log.Log.setverbosity(5)
        Globals.change_source_perms = 1
        SetConnections.UpdateGlobal('checkpoint_interval', 3)
        user_group.init_user_mapping()
        user_group.init_group_mapping()

    def testMirror(self):
        """Testing simple mirror"""
        MirrorTest(None, None, [old_inc1_dir])

    def testMirror2(self):
        """Test mirror with larger data set"""
        MirrorTest(1, None,
                   [old_inc1_dir, old_inc2_dir, old_inc3_dir, old_inc4_dir])

    def testMirror3(self):
        """Local version of testMirror2"""
        MirrorTest(1, 1,
                   [old_inc1_dir, old_inc2_dir, old_inc3_dir, old_inc4_dir])


if __name__ == "__main__":
    unittest.main()
