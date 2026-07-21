# Player Brain + Production Foundation

This patch introduces four additive foundations:

1. `PlayerProfile`
   - Collector mode
   - Normal-quality pet food
   - Manual King handling
   - Game-managed display restocking

2. `CollectionPolicy`
   - Legendary items are permanently protected
   - Non-normal items stay protected until their collection entry is complete
   - Optional per-item permanent keep list

3. `AccountCapabilities`
   - Production/Fusion shared queue capacity: currently 10
   - Expedition team capacity: currently 8
   - Furniture upgrade slots: currently 2
   - Values are updateable and must not be hardcoded in planners

4. `SharedProductionQueue`
   - Craft and Fusion use the same capacity
   - The UI badge represents remaining slots
   - Completed but uncollected items still occupy slots
   - Collecting completed items releases slots
   - Mode switches must be verified by Vision before item selection

This patch is intentionally runtime-agnostic. It does not click the game.
