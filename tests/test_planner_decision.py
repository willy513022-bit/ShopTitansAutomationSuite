import unittest
from core import PlannerDecision
class TestDecision(unittest.TestCase):
 def test_confidence(self):
  with self.assertRaises(ValueError): PlannerDecision('A','B',1,'C',1.1)
 def test_payload_copy(self):
  p={'x':1}; d=PlannerDecision('A','B',1,'C',payload=p); p['x']=2; self.assertEqual(d.payload['x'],1)
if __name__=='__main__': unittest.main()
