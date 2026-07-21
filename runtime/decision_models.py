from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional
from core.planner_decision import PlannerDecision
from vision.popup_models import PopupAction

class RuntimeDecisionKind(str, Enum):
    POPUP_ACTION = 'popup_action'
    DELEGATE_PLANNER = 'delegate_planner'
    WAIT = 'wait'

@dataclass(frozen=True, slots=True)
class RuntimeDecision:
    kind: RuntimeDecisionKind
    reason: str
    popup_action: Optional[PopupAction] = None
    planner_decision: Optional[PlannerDecision] = None
    blocking: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)
    def __post_init__(self):
        reason=self.reason.strip()
        if not reason: raise ValueError('reason is required')
        if self.kind is RuntimeDecisionKind.POPUP_ACTION:
            if self.popup_action is None or self.planner_decision is not None: raise ValueError('popup decisions require only popup_action')
            if not self.blocking: raise ValueError('popup decisions must be blocking')
        elif self.kind is RuntimeDecisionKind.DELEGATE_PLANNER:
            if self.planner_decision is None or self.popup_action is not None: raise ValueError('planner decisions require only planner_decision')
            if self.blocking: raise ValueError('planner delegation cannot be blocking')
        elif self.kind is RuntimeDecisionKind.WAIT:
            if self.popup_action is not None or self.planner_decision is not None: raise ValueError('wait decisions cannot carry an action')
        else: raise TypeError('kind must be RuntimeDecisionKind')
        object.__setattr__(self,'reason',reason)
        object.__setattr__(self,'metadata',MappingProxyType(dict(self.metadata)))
    @property
    def actionable(self): return self.kind is not RuntimeDecisionKind.WAIT
