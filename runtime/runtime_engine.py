from __future__ import annotations

from typing import Optional

from core.planner_decision import PlannerDecision
from world_state.world_state import WorldState

from .decision_bridge import RuntimeDecisionBridge
from .executor import RuntimeExecutor


class RuntimeEngine:
    """
    Runtime 的主控入口。

    每一次 Tick：
        WorldState
            ↓
        DecisionBridge
            ↓
        RuntimeDecision
            ↓
        Executor
    """

    def __init__(
        self,
        executor: RuntimeExecutor,
        bridge: Optional[RuntimeDecisionBridge] = None,
    ) -> None:
        self._executor = executor
        self._bridge = bridge or RuntimeDecisionBridge()

    def tick(
        self,
        world_state: WorldState,
        planner_decision: Optional[PlannerDecision] = None,
    ) -> None:

        decision = self._bridge.decide(
            world_state=world_state,
            planner_decision=planner_decision,
        )

        self._executor.execute(decision)