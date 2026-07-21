import json
from pathlib import Path

from services.official_data_importer import (
    OfficialDataImporter,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

NORMALIZED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "official_database"
    / "normalized"
)


def main() -> None:
    print(
        "Official Data Importer 測試"
    )

    print("=" * 70)

    importer = OfficialDataImporter()

    summary = importer.run()

    print()
    print("匯入完成")
    print("-" * 70)

    print(
        "來源：",
        summary.source_path,
    )

    print(
        "工作表：",
        summary.sheet_count,
    )

    print(
        "Blueprint：",
        summary.blueprint_count,
    )

    print(
        "Worker：",
        summary.worker_count,
    )

    print(
        "Quest Component：",
        summary.quest_component_count,
    )

    print(
        "輸出位置：",
        summary.output_directory,
    )

    items_path = (
        NORMALIZED_DIRECTORY
        / "items.json"
    )

    recipes_path = (
        NORMALIZED_DIRECTORY
        / "recipes.json"
    )

    with items_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        items = json.load(
            file
        )

    with recipes_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        recipes = json.load(
            file
        )

    print()
    print("Items 預覽")
    print("-" * 70)

    for item in items[:10]:
        print(
            f"{item['item_id']:<35} "
            f"{item['name']:<25} "
            f"T{item['tier']:<2} "
            f"{item['item_type']:<15} "
            f"{item['craft_time_seconds']} 秒"
        )

    print()
    print("Recipes 預覽")
    print("-" * 70)

    recipe_by_id = {
        recipe["item_id"]: recipe
        for recipe in recipes
    }

    preview_names = {
        "Squire Sword",
        "Cutlass",
        "Blackthorn Razor",
    }

    item_by_name = {
        item["name"]: item
        for item in items
    }

    for name in preview_names:
        item = item_by_name.get(
            name
        )

        if item is None:
            print(
                name,
                "：找不到",
            )

            continue

        recipe = recipe_by_id.get(
            item["item_id"]
        )

        print()
        print(
            name,
            item["item_id"],
        )

        if recipe is None:
            print(
                "  無 Recipe"
            )

            continue

        for ingredient in recipe[
            "ingredients"
        ]:
            print(
                " ",
                ingredient,
            )

    print()
    print("=" * 70)

    print(
        "V2 game_data 已同步："
    )

    print(
        PROJECT_ROOT
        / "data"
        / "game_data"
        / "items.json"
    )

    print(
        PROJECT_ROOT
        / "data"
        / "game_data"
        / "recipes.json"
    )


if __name__ == "__main__":
    main()