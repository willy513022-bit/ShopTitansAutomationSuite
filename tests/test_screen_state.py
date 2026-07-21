import unittest
from core.screen_state import ScreenState

class TestScreenState(unittest.TestCase):
    def test_members(self):
        self.assertIn(ScreenState.TOWN, list(ScreenState))
        self.assertIn(ScreenState.DISCONNECTED, list(ScreenState))

if __name__=="__main__":
    unittest.main()
