# Navigation Engine V1

This additive patch introduces the first reusable navigation layer.

## Responsibilities

- `Screen`
  - Canonical screen and Production-mode identifiers.

- `ScreenGraph`
  - Stores legal screen transitions.
  - Resolves the lowest-cost route with Dijkstra's algorithm.

- `NavigationStateTracker`
  - Stores the latest Vision-confirmed screen.
  - Rejects low-confidence navigation starts.

- `Navigator`
  - Plans a route only.
  - Does not click the game.
  - Requires Vision to refresh and validate state.

- `NavigationValidator`
  - Confirms each transition target.
  - Distinguishes `ARRIVED`, `WRONG_SCREEN`, and `LOW_CONFIDENCE`.

- `VisionState`
  - Initial normalized state contract shared with future Feature Packs.

## Current Production route

```text
SHOP
  -> PRODUCTION
      -> CRAFT
      -> FUSION
```

Craft/Fusion switching is modeled explicitly because the game uses a shared
Production UI and a shared queue.

## Runtime integration contract

Future runtime integration should follow:

```text
Vision observes current screen
    -> Navigator plans one transition
    -> Runtime executes action
    -> Vision observes again
    -> NavigationValidator confirms target
    -> continue or recover
```

The Navigator must never assume that a click succeeded.
