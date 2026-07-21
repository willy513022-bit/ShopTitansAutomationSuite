from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .strategy import Strategy


@dataclass(frozen=True, slots=True)
class DecisionContext:
    """Immutable snapshot passed to planners and the scheduler.

    It keeps the scheduler independent from Vision, Runtime and concrete game
    state classes.  New feature packs can attach extra values through metadata
    without changing the scheduler API.
    """

    world_state: Any
    strategy: Strategy = field(default_factory=Strategy)
    runtime_modifiers: Mapping[str, float] = field(default_factory=dict)
    rule_ids: tuple[str, ...] = ()
    memory: Any = None
    current_task: Any = None
    event: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        modifiers = {
            str(key): float(value)
            for key, value in self.runtime_modifiers.items()
        }
        if any(not key.strip() for key in modifiers):
            raise ValueError("runtime modifier keys must not be empty")

        object.__setattr__(
            self,
            "runtime_modifiers",
            MappingProxyType(modifiers),
        )
        object.__setattr__(self, "rule_ids", tuple(self.rule_ids))
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    def with_runtime_modifiers(
        self,
        modifiers: Mapping[str, float],
    ) -> "DecisionContext":
        merged = dict(self.runtime_modifiers)
        merged.update(modifiers)
        return DecisionContext(
            world_state=self.world_state,
            strategy=self.strategy,
            runtime_modifiers=merged,
            rule_ids=self.rule_ids,
            memory=self.memory,
            current_task=self.current_task,
            event=self.event,
            metadata=self.metadata,
            observed_at=self.observed_at,
        )
