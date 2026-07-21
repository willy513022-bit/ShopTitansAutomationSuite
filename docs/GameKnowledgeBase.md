# Game Knowledge Base V1

The knowledge base separates verified game data from planner and executor code.

```text
GameKnowledgeBase
├── EventRegistry
├── RecipeRegistry
├── TemplateRegistry
└── ClickMapRegistry
```

## Included verified event definitions

- Guild member gift
- Guild member energy
- Worker item offer
- Spin-ticket bubble
- Daily free spin
- King's Caprice extra craft slot

The definitions are based on the user's descriptions and uploaded gameplay videos.

## Intentionally excluded

- Hot air balloon
- Train

Those systems belong to a different game project and are not part of Shop Titans.

## Empty databases

`data/recipes/items.json` and `data/templates/registry.json` are intentionally empty.
Unverified recipes, names, coordinates, and template paths are not invented.

## Adding an event

Create one JSON file under `data/events/`.
The loader automatically discovers it when the project starts.
