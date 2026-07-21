from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TransactionState(str, Enum):
    PLANNED = "planned"
    EXECUTING = "executing"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    RETRYABLE = "retryable"
    FAILED = "failed"


@dataclass
class ActionTransaction:
    transaction_id: str
    action_name: str
    state: TransactionState = TransactionState.PLANNED
    payload: dict[str, Any] = field(default_factory=dict)
    expected_effects: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    last_error: str | None = None

    def mark_executing(self) -> None:
        self.state = TransactionState.EXECUTING

    def mark_awaiting_confirmation(self) -> None:
        self.state = TransactionState.AWAITING_CONFIRMATION

    def commit(self) -> None:
        self.state = TransactionState.COMMITTED
        self.last_error = None

    def rollback(self, reason: str) -> None:
        self.state = TransactionState.ROLLED_BACK
        self.last_error = reason

    def mark_retryable(self, reason: str) -> None:
        self.retry_count += 1
        self.last_error = reason

        if self.retry_count > self.max_retries:
            self.state = TransactionState.FAILED
        else:
            self.state = TransactionState.RETRYABLE
