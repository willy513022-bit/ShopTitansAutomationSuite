# Planner Architecture

## Pipeline

`Vision -> WorldState -> DecisionContext -> PlannerManager -> PlannerDecision[] -> PriorityEngine -> Scheduler -> Runtime`

## Responsibilities

- **Planner** proposes a candidate. It does not select the winner and never performs input/OCR/runtime work.
- **PriorityEngine** applies Strategy, confidence and runtime modifiers.
- **Scheduler** ranks candidates and selects one winner.
- **Runtime** is the only layer allowed to interact with the game.

## Planner contract

Every planner inherits `BasePlanner` and implements:

```python
@property
def name(self) -> str: ...

def evaluate(self, context: DecisionContext) -> PlannerDecision | None: ...
```

Missing or uncertain facts must return `None`; planners must not guess.

## ProductionPlanner v1

The first production planner consumes a normalized production snapshot containing:

- `free_slots`
- `restock_needed`
- optional `target_item`

It emits a `CRAFT` candidate only when at least one slot is free and restocking is explicitly required.
