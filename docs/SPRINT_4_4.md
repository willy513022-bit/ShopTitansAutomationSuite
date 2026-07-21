# Sprint 4.4 — WorldState Builder

## Goal
Create the immutable boundary between Vision output and planner input.

## Pipeline

`NotificationDetection + PopupDetection + domain states -> WorldStateBuilder -> WorldState`

## Added
- `NotificationState`: one semantic notification per category.
- `WorldState`: immutable planner-safe snapshot.
- `WorldStateBuilder`: parses notifications, resolves popup priority, freezes inputs, and timestamps observations.
- Olympus Superior Pack paid-offer asset variant.

## Safety
A blocking popup makes `WorldState.safe_for_gameplay` false. Reconnect continues to outrank paid offers and upgrade-complete popups.

## Scope
This sprint does not execute clicks and does not change Runtime or Scheduler behavior.
