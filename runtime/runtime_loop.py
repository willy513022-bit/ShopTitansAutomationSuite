from __future__ import annotations

import time
from typing import Optional

from core.planner_decision import PlannerDecision
from runtime.runtime_engine import RuntimeEngine
from world_state.world_state import WorldState


class RuntimeLoop:
    """
    Shop Titans Runtime 主循環。

    目前先負責：
        WorldState
            ↓
        RuntimeEngine

    之後再加入：
        Capture
        VisionEngine
        Scheduler
    """

    def __init__(
        self,
        runtime_engine: RuntimeEngine,
        tick_interval: float = 0.20,
    ) -> None:

        self._runtime = runtime_engine
        self._tick_interval = tick_interval
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False

    def run_once(
        self,
        world_state: WorldState,
        planner_decision: Optional[PlannerDecision] = None,
    ) -> None:

        self._runtime.tick(
            world_state=world_state,
            planner_decision=planner_decision,
        )

    def run_forever(self) -> None:
        """
        暫時只有空迴圈。

        下一個 Sprint
        再接 Capture + VisionEngine。
        """

        self._running = True

        while self._running:

            # TODO:
            # frame = capture()
            # world_state = vision.scan(frame)

            world_state = WorldState()

            self.run_once(world_state)

            time.sleep(self._tick_interval)