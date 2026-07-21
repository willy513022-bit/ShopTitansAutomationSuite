
import unittest
from runtime.capture import Capture
from runtime.click import ClickExecutor
class T(unittest.TestCase):
    def test_capture(self):
        img=Capture().grab()
        self.assertEqual(img.shape,(720,1280,3))
    def test_click(self):
        r=ClickExecutor().click(10,20)
        self.assertEqual(r["mode"],"DRY_RUN")
if __name__=="__main__":
    unittest.main()
