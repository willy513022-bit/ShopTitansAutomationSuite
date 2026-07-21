import unittest
from core import *
class TestScheduler(unittest.TestCase):
 def test_highest(self):
  r=Scheduler().select([PlannerDecision('Collection','DONATE',96,'Ready'),PlannerDecision('LostCity','BOSS',91,'Ready')],Strategy()); self.assertEqual(r.winner.decision.planner,'Collection')
 def test_modifier(self):
  st=Strategy(lost_city_mode=LostCityMode.FULL,planner_modifiers={'lostcity':10}); r=Scheduler().select([PlannerDecision('Collection','DONATE',96,'Ready'),PlannerDecision('LostCity','BOSS',91,'Ready')],st); self.assertEqual(r.winner.decision.planner,'LostCity'); self.assertEqual(st.effective_collection_reserve(),0)
 def test_flag(self):
  st=Strategy(feature_flags={'collection':False,'lostcity':True}); r=Scheduler().select([PlannerDecision('Collection','DONATE',100,'Ready'),PlannerDecision('LostCity','FARM',80,'Ready')],st); self.assertEqual(r.winner.decision.planner,'LostCity'); self.assertEqual(len(r.skipped),1)
 def test_tie(self):
  r=Scheduler().select([PlannerDecision('LostCity','FARM',80,'Ready',.9),PlannerDecision('Collection','DONATE',80,'Ready',1.0)],Strategy()); self.assertEqual(r.winner.decision.planner,'Collection')
 def test_empty(self): self.assertFalse(Scheduler().select([],Strategy()).has_winner)
if __name__=='__main__': unittest.main()
