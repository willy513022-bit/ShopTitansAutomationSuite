import unittest
from recovery.recovery_executor import RecoveryExecutor
class T(unittest.TestCase):
    def test_dry(self):
        ex=RecoveryExecutor()
        r=ex.execute({"action":"RECONNECT"})
        self.assertTrue(r["executed"])
        self.assertEqual(r["mode"],"DRY_RUN")
    def test_none(self):
        ex=RecoveryExecutor()
        r=ex.execute(None)
        self.assertFalse(r["executed"])
if __name__=="__main__":
    unittest.main()
