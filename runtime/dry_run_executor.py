from dataclasses import dataclass
from .decision_models import RuntimeDecision, RuntimeDecisionKind
@dataclass(frozen=True,slots=True)
class RuntimeExecutionResult:
    decision:RuntimeDecision
    executed:bool
    reason:str
class DryRunRuntimeExecutor:
    def execute(self,decision:RuntimeDecision)->RuntimeExecutionResult:
        if not isinstance(decision,RuntimeDecision): raise TypeError('decision must be RuntimeDecision')
        if decision.kind is RuntimeDecisionKind.POPUP_ACTION: detail=decision.popup_action.action_type.value
        elif decision.kind is RuntimeDecisionKind.DELEGATE_PLANNER: detail=decision.planner_decision.action
        else: detail='wait'
        return RuntimeExecutionResult(decision,False,f"Dry Run: recorded '{detail}' without game input")
