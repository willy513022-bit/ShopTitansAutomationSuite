import unittest
from recovery.popup_rules import POPUP_RULES
from core.screen_state import ScreenState

class TestPopupRules(unittest.TestCase):
    def test_offer_rule(self):
        self.assertEqual(POPUP_RULES[ScreenState.LIMITED_OFFER]["action"],"CLOSE_POPUP")

if __name__=="__main__":
    unittest.main()
