
import unittest,time
from core.cooldown import CooldownManager
class T(unittest.TestCase):
    def test_flow(self):
        c=CooldownManager()
        c.start("Collection",1,"test")
        self.assertFalse(c.is_ready("Collection"))
        self.assertGreaterEqual(c.remaining("Collection"),0)
        time.sleep(1.1)
        self.assertTrue(c.is_ready("Collection"))
        c.start("A",5)
        c.start("B",5)
        c.clear("A")
        self.assertTrue(c.is_ready("A"))
        c.clear_all()
        self.assertTrue(c.is_ready("B"))
if __name__=="__main__":
    unittest.main()
