from __future__ import annotations

import time
from collections.abc import Callable
from typing import Optional

from core.planner_decision import PlannerDecision
from runtime.runtime_engine import RuntimeEngine
from world_state.world_state import WorldState


WorldStateProvider = Callable[[], WorldState]
PlannerDecisionProvider = Callable[[WorldState], Optional[PlannerDecision]]


class RuntimeLoop:
    """
    Shop Titans Runtime 主循環。

    RuntimeLoop 不直接負責截圖或影像辨識，
    而是透過 world_state_provider 取得最新 WorldState。

    正式流程：
        Capture / Vision
            ↓
        world_state_provider()
            ↓
        RuntimeEngine.tick()
    """

    def __init__(
        self,
        runtime_engine: RuntimeEngine,
        world_state_provider: Optional[WorldStateProvider] = None,
        planner_decision_provider: Optional[
            PlannerDecisionProvider
        ] = None,
        tick_interval: float = 0.20,
        error_interval: float = 1.00,
    ) -> None:
        if not isinstance(runtime_engine, RuntimeEngine):
            raise TypeError(
                "runtime_engine must be RuntimeEngine"
            )

        if tick_interval <= 0:
            raise ValueError(
                "tick_interval must be greater than 0"
            )

        if error_interval <= 0:
            raise ValueError(
                "error_interval must be greater than 0"
            )

        self._runtime = runtime_engine
        self._world_state_provider = world_state_provider
        self._planner_decision_provider = (
            planner_decision_provider
        )
        self._tick_interval = float(tick_interval)
        self._error_interval = float(error_interval)
        self._running = False
        self._tick_count = 0

    @property
    def running(self) -> bool:
        return self._running

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def stop(self) -> None:
        """要求主循環在目前這一輪結束後停止。"""

        self._running = False

    def run_once(
        self,
        world_state: WorldState,
        planner_decision: Optional[
            PlannerDecision
        ] = None,
    ) -> None:
        """執行單次 Runtime Tick。"""

        if not isinstance(world_state, WorldState):
            raise TypeError(
                "world_state must be WorldState"
            )

        if (
            planner_decision is not None
            and not isinstance(
                planner_decision,
                PlannerDecision,
            )
        ):
            raise TypeError(
                "planner_decision must be "
                "PlannerDecision or None"
            )

        self._runtime.tick(
            world_state=world_state,
            planner_decision=planner_decision,
        )

        self._tick_count += 1

    def run_provider_once(self) -> WorldState:
        """
        從 Provider 取得最新狀態並執行一次。

        回傳本輪使用的 WorldState，
        方便測試與除錯。
        """

        if self._world_state_provider is None:
            raise RuntimeError(
                "world_state_provider is not configured"
            )

        world_state = self._world_state_provider()

        if not isinstance(world_state, WorldState):
            raise TypeError(
                "world_state_provider must return WorldState"
            )

        planner_decision = None

        if self._planner_decision_provider is not None:
            planner_decision = (
                self._planner_decision_provider(
                    world_state
                )
            )

        self.run_once(
            world_state=world_state,
            planner_decision=planner_decision,
        )

        return world_state

    def run_forever(
        self,
        max_ticks: Optional[int] = None,
    ) -> None:
        """
        持續執行 Runtime。

        Ctrl+C 可以安全停止。

        max_ticks:
            測試時可限制執行次數；
            None 代表持續執行直到 stop() 或 Ctrl+C。
        """

        if self._world_state_provider is None:
            raise RuntimeError(
                "world_state_provider is required "
                "for run_forever()"
            )

        if max_ticks is not None and max_ticks <= 0:
            raise ValueError(
                "max_ticks must be greater than 0"
            )

        self._running = True

        print("[RuntimeLoop] Started")
        print("[RuntimeLoop] Press Ctrl+C to stop")

        try:
            while self._running:
                started_at = time.monotonic()

                try:
                    self.run_provider_once()

                except Exception as exc:
                    # 單輪失敗不讓整個 Bot 直接崩潰。
                    print(
                        "[RuntimeLoop] Tick failed: "
                        f"{type(exc).__name__}: {exc}"
                    )

                    time.sleep(self._error_interval)
                    continue

                if (
                    max_ticks is not None
                    and self._tick_count >= max_ticks
                ):
                    self.stop()
                    break

                elapsed = time.monotonic() - started_at
                remaining = self._tick_interval - elapsed

                if remaining > 0:
                    time.sleep(remaining)

        except KeyboardInterrupt:
            print()
            print("[RuntimeLoop] Ctrl+C received")

        finally:
            self._running = False
            print(
                "[RuntimeLoop] Stopped "
                f"after {self._tick_count} ticks"
            )
