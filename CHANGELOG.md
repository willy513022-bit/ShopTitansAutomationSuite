# Changelog

## Sprint 4 — Production Intelligence

- Added evaluator framework and immutable `EvaluationResult`.
- Added inventory-gap and production-queue evaluators.
- Added normalized world-state models for inventory, production, and recipes.
- Upgraded `ProductionPlanner` to compare multiple production candidates.
- Preserved Sprint 3 production snapshot compatibility.
- Added architecture decision record and evaluator/world-state tests.

# Sprint 3 Planner Foundation

- Added planners package, PlannerManager and ProductionPlanner v1.
- Added DecisionTrace explainability support.
- Integrated Sprint 2 DecisionContext API.
- Added planner tests and architecture documentation.

# Changelog

## v0.9.8-alpha.1

- Added canonical `Screen` enum.
- Added explicit transition actions.
- Added weighted `ScreenGraph`.
- Added shortest-path route resolution.
- Added Vision-confidence-aware state tracking.
- Added route-only `Navigator`.
- Added transition and arrival validation.
- Added normalized `VisionState`.
- Added initial Shop/Production/Craft/Fusion routes.
- Added Quest, Guild, Pet, Upgrade, and King placeholder routes.

## Sprint 4.2 — Notification Foundation

- Added raw notification detection models for Craft, Fusion, and Quest.
- Added a generic icon-and-badge `NotificationDetector` built on the existing `TemplateMatcher`.
- Added semantic parsing for category-specific `+` behavior and numeric badges.
- Added isolated unit tests and Sprint 4.2 architecture documentation.
- Preserved existing VisionEngine, Runtime, Planner, and Scheduler behavior.

## Sprint 4.3 — Popup Framework

- Added semantic popup types for reconnect, paid offers, and completed upgrades.
- Added a registry-based detector supporting multiple visual variants per popup type.
- Added popup parsing, runtime-neutral action intent, and semantic priority resolution.
- Added supplied reconnect, paid-offer, and COMPLETE-banner assets.
- Added targeted unit tests while preserving Sprint 4.2 notification behavior.
- Paid offers can only produce a close action; no purchase action is defined.


## v0.4.4 - Sprint 4.4 WorldState Builder

### Added
- Immutable `WorldState` snapshot for planner and scheduler consumption.
- `WorldStateBuilder` integration for Notification and Popup semantics.
- `NotificationState` category aggregation.
- Olympus Superior Pack paid-offer template asset.
- WorldState unit and integration tests.

## v0.4.5 - Sprint 4.5 Runtime Decision Bridge
### Added
- Immutable RuntimeDecision routing model.
- Popup-first RuntimeDecisionBridge.
- Safe WAIT fallback and DryRunRuntimeExecutor.
- Unit tests and Sprint documentation.
### Safety
- No live mouse clicks or keyboard events were added.
