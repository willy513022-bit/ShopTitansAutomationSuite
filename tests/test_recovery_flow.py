import unittest
from recovery.recovery_flow import RecoveryFlow
from core.screen_state import ScreenState

class TestRecoveryFlow(unittest.TestCase):
    def test_success(self):
        f=RecoveryFlow()
        r=f.execute(ScreenState.DISCONNECTED)
        self.assertEqual(r["status"],"RECOVERED")

    def test_unknown(self):
        f=RecoveryFlow()
        r=f.execute(ScreenState.UNKNOWN)
        self.assertEqual(r["status"],"NO_RULE")

if __name__=="__main__":
    unittest.main()
