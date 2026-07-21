from core import PlannerDecision
from core.task_lock import TaskLockManager


def print_state(loop: int, manager: TaskLockManager) -> None:
    current = manager.current()
    print("=" * 60)
    print(f"Loop {loop:03d}")
    if current is None:
        print("Task Lock: OFF")
        return

    print("Task Lock: ON")
    print(f"Continue: {current.planner} -> {current.action}")
    print(f"Reason: {current.reason}")
    remaining = manager.remaining_seconds()
    if remaining is None:
        print("Timeout: none")
    else:
        print(f"Remaining: {remaining:.1f}s")


def main() -> None:
    manager = TaskLockManager()
    decision = PlannerDecision(
        planner="LostCity",
        action="START_BOSS_QUEST",
        base_priority=90,
        reason="Boss first-clear is available",
        task_lock=True,
        estimated_seconds=300,
        interruptible=False,
        payload={"quest_id": "boss"},
        rule_ids=("LC-001", "LC-003"),
    )

    print_state(1, manager)
    print("Winner: LostCity -> START_BOSS_QUEST")
    manager.acquire_for_decision(decision)

    print_state(2, manager)
    print("Scheduler should continue the locked flow instead of voting again.")

    print_state(3, manager)
    print("Validator: battle settlement completed and town is stable.")
    manager.release(planner="LostCity", action="START_BOSS_QUEST")

    print_state(4, manager)
    print("Scheduler may select a new winner.")
    print("=" * 60)


if __name__ == "__main__":
    main()
