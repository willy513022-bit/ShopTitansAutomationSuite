import unittest
from core.ai_context import AIContext

class TestAIContext(unittest.TestCase):
    def test_defaults(self):
        c=AIContext()
        self.assertFalse(c.summary()["has_game_state"])
    def test_settings(self):
        c=AIContext(settings={"auto_craft":True})
        self.assertTrue(c.settings["auto_craft"])

if __name__=="__main__":
    unittest.main()
