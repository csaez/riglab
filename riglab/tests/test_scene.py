import sys
import unittest
from mock import MagicMock

# patch maya dependencies
sys.modules["maya"] = MagicMock()
sys.modules["naming"] = MagicMock()
sys.modules["riglab.rig"] = MagicMock()

from riglab import scene


class TestScene(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_exists(self):
        self.assertTrue(scene.exists("my_rig"))


if __name__ == "__main__":
    unittest.main()
