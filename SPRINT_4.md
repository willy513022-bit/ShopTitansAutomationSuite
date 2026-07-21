# Sprint 4 — Production Intelligence

## Delivered

- `evaluators/` foundation
- immutable `EvaluationResult`
- `InventoryEvaluator`
- `QueueEvaluator`
- normalized production, inventory and recipe state models
- multi-candidate selection in `ProductionPlanner`
- explainable score factors embedded in `PlannerDecision.payload`
- backwards compatibility with the Sprint 3 production snapshot
- ADR and unit tests

## Preferred input

```python
DecisionContext(
    world_state={
        "production": {
            "free_slots": 2,
            "candidates": [
                {"item": "Wood Axe", "current_stock": 4, "target_stock": 20},
                {"item": "Squire Sword", "current_stock": 18, "target_stock": 20},
            ],
        }
    }
)
```

The planner selects the eligible candidate with the highest combined evaluator score. Ties are deterministic by item name.
