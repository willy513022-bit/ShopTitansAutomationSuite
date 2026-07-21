# Architecture

```text
GameData v2
  ├─ item_id
  ├─ name
  ├─ tier
  ├─ craft_time
  └─ recipe dependencies

Screen Perception
  InventoryDetector → TierBadgeDetector → InventoryCardLocator
  → Name ROI / Quantity ROI
  → OCR + ItemNameMatcher + QualityDetector

Inventory Identity = item_id + quality
Inventory Snapshot → Craft Planner → Craft Queue → Action / Verify Loop
```
