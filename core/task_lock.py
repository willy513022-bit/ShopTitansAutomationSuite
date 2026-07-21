from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Callable

from .planner_decision import PlannerDecision


class TaskLockError(RuntimeError):
    """Base exception for invalid task-lock operations."""


class TaskLockAlreadyActiveError(TaskLockError):
    """Raised when a new owner attempts to replace an active lock."""


class TaskLockOwnershipError(TaskLockError):
    """Raised when a non-owner attempts to release or refresh a lock."""


@dataclass(frozen=True, slots=True)
class TaskLockSnapshot:
    """Read-only view of the currently locked task."""

    planner: str
    action: str
    reason: str
    acquired_at: float
    expires_at: float | None
    interruptible: bool
    payload: dict[str, object]

    def remaining(self, now: float) -> float | None:
        if self.expires_at is None:
            return None
        return max(0.0, self.expires_at - now)


class TaskLockManager:
    """Owns one uninterruptible planner task at a time.

    The manager contains no Shop Titans gameplay logic.  A flow acquires the
    lock before starting a multi-step action and releases it only after the
    action has been validated as complete.

    A monotonic clock can be injected for deterministic unit tests.
    """

    def __init__(self, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._lock = RLock()
        self._snapshot: TaskLockSnapshot | None = None

    def acquire(
        self,
        *,
        planner: str,
        action: str,
        reason: str,
        timeout_seconds: float | None = None,
        interruptible: bool = False,
        payload: dict[str, object] | None = None,
        replace_if_same_owner: bool = True,
    ) -> TaskLockSnapshot:
        planner = planner.strip()
        action = action.strip()
        reason = reason.strip()

        if not planner:
            raise ValueError("planner must not be empty")
        if not action:
            raise ValueError("action must not be empty")
        if not reason:
            raise ValueError("reason must not be empty")
        if timeout_seconds is not None and timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        with self._lock:
            self._discard_expired_unlocked()
            active = self._snapshot
            if active is not None:
                same_owner = (
                    active.planner.casefold() == planner.casefold()
                    and active.action.casefold() == action.casefold()
                )
                if not (same_owner and replace_if_same_owner):
                    raise TaskLockAlreadyActiveError(
                        f"task lock is owned by {active.planner}:{active.action}"
                    )

            now = self._clock()
            expires_at = (
                None if timeout_seconds is None else now + timeout_seconds
            )
            snapshot = TaskLockSnapshot(
                planner=planner,
                action=action,
                reason=reason,
                acquired_at=now,
                expires_at=expires_at,
                interruptible=interruptible,
                payload=dict(payload or {}),
            )
            self._snapshot = snapshot
            return snapshot

    def acquire_for_decision(
        self,
        decision: PlannerDecision,
        *,
        timeout_seconds: float | None = None,
        reason: str | None = None,
    ) -> TaskLockSnapshot:
        """Acquire a lock directly from a selected planner decision."""

        resolved_timeout = timeout_seconds
        if resolved_timeout is None and decision.estimated_seconds > 0:
            resolved_timeout = decision.estimated_seconds

        return self.acquire(
            planner=decision.planner,
            action=decision.action,
            reason=reason or decision.reason,
            timeout_seconds=resolved_timeout,
            interruptible=decision.interruptible,
            payload=dict(decision.payload),
        )

    def release(
        self,
        *,
        planner: str | None = None,
        action: str | None = None,
        force: bool = False,
    ) -> TaskLockSnapshot | None:
        """Release and return the previous lock.

        Supplying planner/action protects against an unrelated flow unlocking
        somebody else's task.  Recovery may use force=True after resync.
        """

        with self._lock:
            self._discard_expired_unlocked()
            active = self._snapshot
            if active is None:
                return None

            if not force:
                if planner is not None and active.planner.casefold() != planner.strip().casefold():
                    raise TaskLockOwnershipError(
                        f"lock belongs to planner {active.planner}, not {planner}"
                    )
                if action is not None and active.action.casefold() != action.strip().casefold():
                    raise TaskLockOwnershipError(
                        f"lock belongs to action {active.action}, not {action}"
                    )

            self._snapshot = None
            return active

    def refresh(
        self,
        timeout_seconds: float,
        *,
        planner: str | None = None,
        action: str | None = None,
    ) -> TaskLockSnapshot:
        """Extend an active lock from the current moment."""

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        with self._lock:
            self._discard_expired_unlocked()
            active = self._snapshot
            if active is None:
                raise TaskLockError("no active task lock to refresh")

            if planner is not None and active.planner.casefold() != planner.strip().casefold():
                raise TaskLockOwnershipError(
                    f"lock belongs to planner {active.planner}, not {planner}"
                )
            if action is not None and active.action.casefold() != action.strip().casefold():
                raise TaskLockOwnershipError(
                    f"lock belongs to action {active.action}, not {action}"
                )

            refreshed = TaskLockSnapshot(
                planner=active.planner,
                action=active.action,
                reason=active.reason,
                acquired_at=active.acquired_at,
                expires_at=self._clock() + timeout_seconds,
                interruptible=active.interruptible,
                payload=dict(active.payload),
            )
            self._snapshot = refreshed
            return refreshed

    def current(self) -> TaskLockSnapshot | None:
        with self._lock:
            self._discard_expired_unlocked()
            return self._snapshot

    def is_active(self) -> bool:
        return self.current() is not None

    def is_owned_by(self, planner: str, action: str | None = None) -> bool:
        active = self.current()
        if active is None:
            return False
        if active.planner.casefold() != planner.strip().casefold():
            return False
        return action is None or active.action.casefold() == action.strip().casefold()

    def remaining_seconds(self) -> float | None:
        active = self.current()
        if active is None:
            return 0.0
        return active.remaining(self._clock())

    def clear_expired(self) -> TaskLockSnapshot | None:
        """Explicitly clear and return an expired lock, when one exists."""

        with self._lock:
            active = self._snapshot
            if active is None or not self._is_expired_unlocked(active):
                return None
            self._snapshot = None
            return active

    def _discard_expired_unlocked(self) -> None:
        if self._snapshot is not None and self._is_expired_unlocked(self._snapshot):
            self._snapshot = None

    def _is_expired_unlocked(self, snapshot: TaskLockSnapshot) -> bool:
        return (
            snapshot.expires_at is not None
            and self._clock() >= snapshot.expires_at
        )
