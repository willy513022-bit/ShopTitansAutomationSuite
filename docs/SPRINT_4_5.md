# Sprint 4.5 — Runtime Decision Bridge

Connects immutable `WorldState` snapshots to runtime-neutral decisions without sending keyboard or mouse input.

Routing order:
1. Blocking popup action
2. Existing planner decision
3. Safe WAIT fallback

Added: `runtime/decision_models.py`, `runtime/decision_bridge.py`, and `runtime/dry_run_executor.py`.

Safety: this sprint is dry-run only. Live execution remains disabled.
