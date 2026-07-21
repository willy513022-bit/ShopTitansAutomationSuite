# TaskLockManager

Commit: `feat(core): add TaskLockManager`

## Responsibility

`TaskLockManager` keeps one multi-step task focused until its flow is either:

- validated as complete and released;
- timed out;
- force-released by Recovery after a screen resynchronization.

It contains no game-specific scheduling rules and is not yet integrated into
`Scheduler` in this commit.

## Typical use

```python
lock_manager.acquire_for_decision(winner.decision)

while lock_manager.is_active():
    continue_current_flow()

lock_manager.release(
    planner="LostCity",
    action="START_BOSS_QUEST",
)
```

The battle lock should be released only after the settlement chain is complete
and a stable town screen has been validated.
