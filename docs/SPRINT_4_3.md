# Sprint 4.3 — Popup Framework

## Goal

Add a registry-based popup Vision domain without coupling OpenCV to Runtime,
Planner, Scheduler, or WorldState.

## Pipeline

```text
Screenshot
  -> PopupDetector
  -> PopupDetection
  -> PopupParser
  -> PopupState
  -> PopupAction
```

## Supported semantic types

| PopupType | Known variants | Intended action | Priority |
|---|---|---|---:|
| `RECONNECT` | Error 1000, Error 4006 | reconnect | 300 |
| `PAID_OFFER` | Limited Time Offer, Naya Offer | close safely | 200 |
| `UPGRADE_FINISHED` | COMPLETE variants | collect/acknowledge | 100 |

Priority is semantic. A lower-confidence reconnect still outranks a
higher-confidence paid offer or upgrade banner.

## Design boundaries

- Detector reports visual facts only.
- Parser assigns meaning and action intent.
- Priority resolver chooses what should be handled first.
- Runtime execution and click coordinates are intentionally deferred.
- No purchase action exists. Paid offers only map to `CLOSE_OFFER`.

## Asset strategy

Multiple images can be registered under one popup type. The detector returns the
best matching variant for each semantic type, keeping error numbers, prices, and
campaign names out of Runtime logic.

## Deferred

- automatic asset-directory loading
- ROI configuration
- click-coordinate registry integration
- VisionEngine integration
- WorldStateBuilder integration
- live-game confidence calibration
