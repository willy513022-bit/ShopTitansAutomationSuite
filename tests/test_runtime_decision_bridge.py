from core.planner_decision import PlannerDecision
from runtime.decision_bridge import RuntimeDecisionBridge
from runtime.decision_models import RuntimeDecisionKind
from vision.popup_models import PopupPriority,PopupState,PopupType
from world_state import WorldState

def popup(t=PopupType.PAID_OFFER):
 p={PopupType.RECONNECT:PopupPriority.RECONNECT,PopupType.PAID_OFFER:PopupPriority.PAID_OFFER,PopupType.UPGRADE_FINISHED:PopupPriority.UPGRADE_FINISHED}
 return PopupState(t,p[t],True,.91,'fixture')
def test_popup_wins_over_planner_decision():
 d=RuntimeDecisionBridge().decide(WorldState(popup=popup(PopupType.RECONNECT)),PlannerDecision('Production','CRAFT',99,'low'));assert d.kind is RuntimeDecisionKind.POPUP_ACTION and d.popup_action.action_type.value=='reconnect' and d.planner_decision is None
def test_paid_offer_maps_to_close_offer():
 d=RuntimeDecisionBridge().decide(WorldState(popup=popup()));assert d.popup_action.action_type.value=='close_offer' and d.blocking
def test_safe_world_delegates_planner_unchanged():
 p=PlannerDecision('Production','CRAFT',42,'low');d=RuntimeDecisionBridge().decide(WorldState(),p);assert d.kind is RuntimeDecisionKind.DELEGATE_PLANNER and d.planner_decision is p
def test_empty_safe_world_waits():
 d=RuntimeDecisionBridge().decide(WorldState());assert d.kind is RuntimeDecisionKind.WAIT and not d.blocking
