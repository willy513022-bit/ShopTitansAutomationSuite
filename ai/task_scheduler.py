from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ai.action import Action


@dataclass
class ScheduledAction:
    action: Action
    created_at: datetime = field(
        default_factory=lambda: (
            datetime.now(timezone.utc)
        )
    )


class TaskScheduler:
    def __init__(self) -> None:
        self._queue: list[
            ScheduledAction
        ] = []

    def enqueue(
        self,
        action: Action,
    ) -> None:
        self._queue.append(
            ScheduledAction(action=action)
        )

        self._queue.sort(
            key=lambda item: (
                item.action.score
            ),
            reverse=True,
        )

    def next_action(
        self,
    ) -> Action | None:
        if not self._queue:
            return None

        return self._queue.pop(0).action

    def clear(self) -> None:
        self._queue.clear()

    def __len__(self) -> int:
        return len(self._queue)
