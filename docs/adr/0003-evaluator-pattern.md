# ADR 0003: Evaluator Pattern

## Status
Accepted for Sprint 4.

## Decision
Production scoring is split into small evaluator classes. Each evaluator receives a `DecisionContext` and a candidate, and returns an immutable `EvaluationResult` containing:

- score
- reason
- rule IDs
- structured details
- eligibility

Planners aggregate evaluator results but do not operate the game. Runtime remains the only layer allowed to click or press keys.

## Consequences

- Every score contribution can be tested independently.
- Replay can show why an item won.
- Missing or unsafe facts can mark a candidate ineligible instead of forcing a guess.
- New production concerns can be added without rewriting Scheduler.
