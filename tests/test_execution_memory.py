import unittest
from core.execution_memory import ExecutionMemory

class T(unittest.TestCase):
    def test_flow(self):
        m=ExecutionMemory()
        m.start("LostCity","START_BOSS")
        self.assertIsNotNone(m.current())
        r=m.finish(True,"done")
        self.assertTrue(r.success)
        self.assertEqual(m.last().reason,"done")
        self.assertEqual(len(m.history()),1)
        m.clear()
        self.assertEqual(len(m.history()),0)

if __name__=="__main__":
    unittest.main()
