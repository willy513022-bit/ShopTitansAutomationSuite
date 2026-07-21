# Sprint 4.2 — Notification Foundation

## Goal

Add a small, reusable notification domain layer without changing runtime,
planner, scheduler, or existing screen detection behavior.

## Pipeline

```text
NotificationDetector
        ↓ raw visual result
NotificationDetection(category, badge, confidence)
        ↓
NotificationParser
        ↓ semantic model
ProductionNotification / QuestNotification
```

## Semantics

| Category | Badge | Meaning |
|---|---:|---|
| Craft | `+` | Empty production slot is available |
| Fusion | `+` | Empty fusion slot is available |
| Craft/Fusion | `1`–`10` | Number of finished jobs |
| Quest | `+` | A new quest is available |
| Quest | `1`–`8` | Quest notification count |

The detector intentionally does not interpret `+`. This keeps computer vision
separate from game rules.

## Added files

- `vision/notification_models.py`
- `vision/notification_parser.py`
- `vision/notification_detector.py`
- `tests/test_notification_models.py`
- `tests/test_notification_parser.py`
- `tests/test_notification_detector.py`

## Test command

```bat
python -m pytest tests\test_notification_models.py tests\test_notification_parser.py tests\test_notification_detector.py -v
```

## Not included yet

- Loading notification templates from disk
- Cropping category-specific ROIs
- VisionEngine integration
- WorldState integration
- Runtime actions

Those are intentionally deferred so this sprint remains backward-compatible
and independently testable.
