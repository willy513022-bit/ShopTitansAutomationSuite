import json
from pathlib import Path

from services.official_importer import OfficialImporter


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

GAME_DATA_ROOT = (
    PROJECT_ROOT
    / "data"
    / "game_data"
)


def main() -> None:
    print("Resource Mapping 測試")
    print("=" * 70)

    summary = OfficialImporter().run()

    print(
        "Blueprint：",
        summary.blueprint_count,
    )

    with (
        GAME_DATA_ROOT
        / "items.json"
    ).open(
        "r",
        encoding="utf-8",
    ) as file:
        items = json.load(file)

    with (
        GAME_DATA_ROOT
        / "recipes.json"
    ).open(
        "r",
        encoding="utf-8",
    ) as file:
        recipes = json.load(file)

    item_by_name = {
        item["name"]: item
        for item in items
    }

    recipe_by_id = {
        recipe["item_id"]: recipe
        for recipe in recipes
    }

    for name in (
        "Squire Sword",
        "Cutlass",
        "Blackthorn Razor",
    ):
        item = item_by_name[name]
        recipe = recipe_by_id[
            item["item_id"]
        ]

        print()
        print(name)

        for ingredient in recipe[
            "ingredients"
        ]:
            print(
                f"  {ingredient['name']:<25} "
                f"× {ingredient['quantity']}"
            )


if __name__ == "__main__":
    main()
