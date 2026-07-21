# Vision Runtime

This commit introduces the first reusable vision pipeline:

```text
Screenshot
    ↓
TemplateMatcher
    ↓
ScreenDetector
    ↓
ScreenClassifier
    ↓
VisionEngine
    ↓
VisionValidator
```

## Scope

This version uses OpenCV template matching and in-memory templates.

It does not yet include:

- live Shop Titans screenshot capture
- production template images
- ROI configuration
- scale-invariant matching
- mouse or ADB integration

## Main classes

- `TemplateMatcher`
- `ScreenDetector`
- `ScreenClassifier`
- `VisionEngine`
- `VisionValidator`
