from __future__ import annotations
from typing import Optional
from core.planner_decision import PlannerDecision
from vision.popup_parser import PopupParser
from world_state.world_state import WorldState
from .decision_models import RuntimeDecision, RuntimeDecisionKind

class RuntimeDecisionBridge:
    def __init__(self,popup_parser:Optional[PopupParser]=None): self.popup_parser=popup_parser or PopupParser()
    def decide(self,world_state:WorldState,planner_decision:Optional[PlannerDecision]=None)->RuntimeDecision:
        if not isinstance(world_state,WorldState): raise TypeError('world_state must be WorldState')
        if planner_decision is not None and not isinstance(planner_decision,PlannerDecision): raise TypeError('planner_decision must be PlannerDecision or None')
        if world_state.popup is not None:
            action=self.popup_parser.action_for(world_state.popup)
            return RuntimeDecision(kind=RuntimeDecisionKind.POPUP_ACTION,popup_action=action,blocking=True,reason=f"Blocking popup '{world_state.popup.popup_type.value}' must be handled before normal gameplay",metadata={'source_template_id':world_state.popup.source_template_id,'popup_confidence':world_state.popup.confidence,'observed_at':world_state.observed_at.isoformat()})
        if planner_decision is not None:
            return RuntimeDecision(kind=RuntimeDecisionKind.DELEGATE_PLANNER,planner_decision=planner_decision,reason=f'WorldState is safe; delegate to {planner_decision.planner}',metadata={'observed_at':world_state.observed_at.isoformat()})
        return RuntimeDecision(kind=RuntimeDecisionKind.WAIT,reason='No blocking popup and no planner decision; wait safely',metadata={'observed_at':world_state.observed_at.isoformat()})
