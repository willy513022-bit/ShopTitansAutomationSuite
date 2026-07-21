from __future__ import annotations

from typing import Protocol

from ai.action import Action


class ActionHandler(Protocol):
    def execute(
        self,
        action: Action,
    ) -> bool:
        ...


class DryRunActionExecutor:
    def execute(
        self,
        action: Action,
    ) -> bool:
        print(
            f"[DRY RUN] "
            f"{action.action_type.value} "
            f"score={action.score:.1f}"
        )

        print(
            "reason:",
            action.reason,
        )

        if action.payload:
            print(
                "payload:",
                action.payload,
            )

        return True
