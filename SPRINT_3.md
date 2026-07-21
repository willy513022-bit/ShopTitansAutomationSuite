# Sprint 3 — Planner Foundation

## Added

- Shared `BasePlanner` contract
- `PlannerManager` registration, collection, failure isolation and Scheduler integration
- Conservative `ProductionPlanner` v1
- `DecisionTrace` explainability adapter
- Planner architecture documentation
- Unit and integration tests

## Compatibility

- Existing `Scheduler.select()` remains unchanged.
- Sprint 2 `DecisionContext` and `Scheduler.select_context()` are included.
- No Runtime, Vision, OCR or GUI module was replaced.

## Test

```bat
python -m unittest tests.test_planner_decision tests.test_scheduler tests.test_task_lock tests.test_decision_context tests.test_planner_manager tests.test_production_planner tests.test_explain -v
```
