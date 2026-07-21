import json
from pathlib import Path

from services.official_importer import (
    OfficialImporter,
)


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
    print("Official Importer V2 測試")
    print("=" * 70)

    summary = (
        OfficialImporter()
        .run()
    )

    print()
    print("匯入完成")
    print("-" * 70)

    print(
        "工作表：",
        summary.sheet_count,
    )

    print(
        "Blueprint：",
        summary.blueprint_count,
    )

    print(
        "Items：",
        summary.item_count,
    )

    print(
        "Recipes：",
        summary.recipe_count,
    )

    print(
        "Workers：",
        summary.worker_count,
    )

    print(
        "輸出：",
        summary.output_directory,
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

    print()
    print("預覽")
    print("-" * 70)

    for name in (
        "Squire Sword",
        "Cutlass",
        "Blackthorn Razor",
    ):
        item = item_by_name.get(name)

        if item is None:
            print(name, "找不到")
            continue

        print()
        print(
            item["item_id"],
            item["name"],
            "T",
            item["tier"],
            item["item_type"],
        )

        recipe = recipe_by_id.get(
            item["item_id"]
        )

        if recipe:
            for ingredient in (
                recipe["ingredients"]
            ):
                print(
                    " ",
                    ingredient,
                )


if __name__ == "__main__":
    main()