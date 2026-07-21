from __future__ import annotations
from typing import Mapping
from .planner_decision import PlannerDecision, ScoredDecision
from .strategy import Strategy

class PriorityEngine:
    def score(self, decision:PlannerDecision, strategy:Strategy, runtime_modifiers:Mapping[str,float]|None=None)->ScoredDecision:
        p=decision.planner.lower(); a=decision.action.upper()
        mods={'planner':strategy.planner_modifiers.get(p,0.0),'action':strategy.action_modifiers.get(a,0.0),'confidence':decision.confidence*strategy.confidence_weight,'runtime':0.0}
        if runtime_modifiers: mods['runtime']=runtime_modifiers.get(p,0.0)+runtime_modifiers.get(a,0.0)
        return ScoredDecision(decision, decision.base_priority+sum(mods.values()), mods)
