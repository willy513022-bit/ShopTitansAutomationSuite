import unittest
from recovery.recovery_planner import RecoveryPlanner
from core.screen_state import ScreenState

class TestRecoveryPlanner(unittest.TestCase):
    def test_known(self):
        p=RecoveryPlanner()
        d=p.plan(ScreenState.DISCONNECTED)
        self.assertEqual(d["action"],"RECONNECT")
    def test_unknown(self):
        p=RecoveryPlanner()
        self.assertIsNone(p.plan(ScreenState.UNKNOWN))

if __name__=="__main__":
    unittest.main()
