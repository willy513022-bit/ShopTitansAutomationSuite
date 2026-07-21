import unittest

from core import PlannerDecision
from core.task_lock import (
    TaskLockAlreadyActiveError,
    TaskLockManager,
    TaskLockOwnershipError,
)


class FakeClock:
    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class TaskLockManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.manager = TaskLockManager(clock=self.clock)

    def test_acquire_and_release(self) -> None:
        lock = self.manager.acquire(
            planner="LostCity",
            action="START_BOSS",
            reason="Battle flow is running",
            timeout_seconds=300,
        )

        self.assertTrue(self.manager.is_active())
        self.assertEqual(lock.planner, "LostCity")
        released = self.manager.release(planner="LostCity", action="START_BOSS")
        self.assertEqual(released, lock)
        self.assertFalse(self.manager.is_active())

    def test_timeout_automatically_expires(self) -> None:
        self.manager.acquire(
            planner="LostCity",
            action="WAIT_FOR_BATTLE",
            reason="Waiting for battle result",
            timeout_seconds=10,
        )

        self.clock.advance(9)
        self.assertTrue(self.manager.is_active())
        self.clock.advance(1)
        self.assertFalse(self.manager.is_active())
        self.assertEqual(self.manager.remaining_seconds(), 0.0)

    def test_different_owner_cannot_replace_active_lock(self) -> None:
        self.manager.acquire(
            planner="LostCity",
            action="START_BOSS",
            reason="Running",
        )

        with self.assertRaises(TaskLockAlreadyActiveError):
            self.manager.acquire(
                planner="GuildHelp",
                action="HELP_ALL",
                reason="Requests are waiting",
            )

    def test_wrong_owner_cannot_release(self) -> None:
        self.manager.acquire(
            planner="LostCity",
            action="START_BOSS",
            reason="Running",
        )

        with self.assertRaises(TaskLockOwnershipError):
            self.manager.release(planner="GuildHelp")
        self.assertTrue(self.manager.is_active())

    def test_force_release_is_available_for_recovery(self) -> None:
        self.manager.acquire(
            planner="LostCity",
            action="START_BOSS",
            reason="Running",
        )

        released = self.manager.release(force=True)
        self.assertEqual(released.planner, "LostCity")
        self.assertFalse(self.manager.is_active())

    def test_refresh_extends_timeout_from_now(self) -> None:
        self.manager.acquire(
            planner="LostCity",
            action="WAIT_FOR_BATTLE",
            reason="Running",
            timeout_seconds=10,
        )
        self.clock.advance(5)

        refreshed = self.manager.refresh(
            20,
            planner="LostCity",
            action="WAIT_FOR_BATTLE",
        )

        self.assertEqual(refreshed.expires_at, 125.0)
        self.clock.advance(19)
        self.assertTrue(self.manager.is_active())
        self.clock.advance(1)
        self.assertFalse(self.manager.is_active())

    def test_acquire_for_decision_uses_decision_metadata(self) -> None:
        decision = PlannerDecision(
            planner="LostCity",
            action="START_BOSS_QUEST",
            base_priority=90,
            reason="Boss first-clear is available",
            payload={"quest_id": "boss"},
            task_lock=True,
            estimated_seconds=180,
            interruptible=False,
        )

        lock = self.manager.acquire_for_decision(decision)

        self.assertEqual(lock.planner, decision.planner)
        self.assertEqual(lock.payload["quest_id"], "boss")
        self.assertEqual(lock.expires_at, 280.0)
        self.assertFalse(lock.interruptible)


if __name__ == "__main__":
    unittest.main()
