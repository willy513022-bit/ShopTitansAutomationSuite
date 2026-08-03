from __future__ import annotations

from .decision_models import RuntimeDecision, RuntimeDecisionKind
from .input_driver import InputDriver
from .target_resolver import TargetResolver


class RuntimeExecutor:
    """
    執行 RuntimeDecision。

    第一版只負責 PopupAction。
    """

    def __init__(
        self,
        resolver: TargetResolver,
        driver: InputDriver,
    ) -> None:
        self._resolver = resolver
        self._driver = driver

    def execute(self, decision: RuntimeDecision) -> None:
        if decision.kind is RuntimeDecisionKind.WAIT:
            print("[Executor] WAIT")
            return

        if decision.kind is RuntimeDecisionKind.DELEGATE_PLANNER:
            planner = decision.planner_decision
            print(f"[Executor] Delegate planner: {planner}")
            return

        action = decision.popup_action
        if action is None:
            raise RuntimeError("Popup decision missing popup_action")

        target = self._resolver.resolve(action.target_name)

        print(
            f"[Executor] {action.action_type.value} "
            f"-> {target.name} "
            f"({target.x}, {target.y})"
        )

        self._driver.click(target.x, target.y)