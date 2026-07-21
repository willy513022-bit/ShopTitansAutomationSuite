import pytest
from core.planner_decision import PlannerDecision
from runtime.decision_models import RuntimeDecision,RuntimeDecisionKind
from vision.popup_models import PopupAction,PopupActionType,PopupPriority,PopupType

def action(): return PopupAction(PopupActionType.RECONNECT,PopupType.RECONNECT,'reconnect_button',PopupPriority.RECONNECT,.95)
def test_popup_runtime_decision_is_actionable_and_freezes_metadata():
 m={'source':'vision'}; d=RuntimeDecision(RuntimeDecisionKind.POPUP_ACTION,'recover',popup_action=action(),blocking=True,metadata=m);m['source']='changed';assert d.actionable and d.metadata['source']=='vision'
def test_runtime_decision_rejects_mixed_payloads():
 p=PlannerDecision('Production','CRAFT',10,'stock low')
 with pytest.raises(ValueError): RuntimeDecision(RuntimeDecisionKind.POPUP_ACTION,'invalid',action(),p,True)
def test_wait_decision_is_not_actionable(): assert not RuntimeDecision(RuntimeDecisionKind.WAIT,'idle').actionable
