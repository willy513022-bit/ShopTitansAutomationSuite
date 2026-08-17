from __future__ import annotations

import json

from models.game_item import (
    GameItem,
    RecipeIngredient,
    WorkerRequirement,
)
from services.game_data_service import (
    GameDataService,
)


def write_data(
    directory,
    *,
    items,
    recipes,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        directory
        / "items.json"
    ).write_text(
        json.dumps(
            items,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (
        directory
        / "recipes.json"
    ).write_text(
        json.dumps(
            recipes,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def make_fixture(
    tmp_path,
):
    data_dir = (
        tmp_path
        / "game_data"
    )

    items = [
        {
            "item_id": (
                "herbal_medicine_"
                "opulent_decoction"
            ),
            "name": (
                "Opulent Decoction"
            ),
            "item_type": (
                "Herbal Medicine"
            ),
            "tier": 12,
            "craft_time_seconds": 66600,
            "base_value": 123456,
            "required_workers": [
                {
                    "worker": (
                        "Herbalist"
                    ),
                    "level": 29,
                },
                {
                    "worker": (
                        "Priestess"
                    ),
                    "level": 25,
                },
                {
                    "worker": (
                        "Wizard"
                    ),
                    "level": 22,
                },
            ],
        },
        {
            "item_id": (
                "hat_ice_queens_"
                "summer_hat"
            ),
            "name": (
                "Ice Queen's Summer Hat"
            ),
            "item_type": "Hat",
            "tier": 10,
            "craft_time_seconds": 3600,
            "base_value": 50000,
            "required_workers": [],
        },
    ]

    recipes = [
        {
            "item_id": (
                "herbal_medicine_"
                "opulent_decoction"
            ),
            "ingredients": [
                {
                    "item_id": None,
                    "name": (
                        "Opulent Jewel"
                    ),
                    "quantity": 6,
                    "quality": "normal",
                    "resource_type": (
                        "quest_component"
                    ),
                },
                {
                    "item_id": None,
                    "name": (
                        "Precious Shell"
                    ),
                    "quantity": 5,
                    "quality": None,
                    "resource_type": (
                        "quest_component"
                    ),
                },
                {
                    "item_id": None,
                    "name": "Herbs",
                    "quantity": 387,
                    "quality": None,
                    "resource_type": (
                        "resource"
                    ),
                    "source_column": "Y",
                },
                {
                    "item_id": None,
                    "name": "Oil",
                    "quantity": 113,
                    "quality": None,
                    "resource_type": (
                        "resource"
                    ),
                    "source_column": "AA",
                },
            ],
        },
        {
            "item_id": (
                "hat_ice_queens_"
                "summer_hat"
            ),
            "ingredients": [],
        },
    ]

    write_data(
        data_dir,
        items=items,
        recipes=recipes,
    )

    return data_dir


def test_get_by_name_loads_metadata(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_name(
        "Opulent Decoction"
    )

    assert isinstance(
        item,
        GameItem,
    )

    assert item is not None

    assert item.tier == 12

    assert (
        item.item_type
        == "Herbal Medicine"
    )

    assert (
        item.craft_time_seconds
        == 66600
    )

    assert (
        item.base_value
        == 123456
    )


def test_required_workers_are_preserved(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_name(
        "Opulent Decoction"
    )

    assert item is not None

    assert item.required_workers == (
        WorkerRequirement(
            worker="Herbalist",
            level=29,
        ),
        WorkerRequirement(
            worker="Priestess",
            level=25,
        ),
        WorkerRequirement(
            worker="Wizard",
            level=22,
        ),
    )


def test_quest_component_preserves_quality(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_name(
        "Opulent Decoction"
    )

    assert item is not None

    jewel = next(
        ingredient
        for ingredient
        in item.ingredients
        if ingredient.name
        == "Opulent Jewel"
    )

    assert isinstance(
        jewel,
        RecipeIngredient,
    )

    assert jewel.item_id is None
    assert jewel.quantity == 6

    assert (
        jewel.resource_type
        == "quest_component"
    )

    assert jewel.quality == "normal"


def test_raw_resource_preserves_source_column(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_name(
        "Opulent Decoction"
    )

    assert item is not None

    herbs = next(
        ingredient
        for ingredient
        in item.ingredients
        if ingredient.name
        == "Herbs"
    )

    assert herbs.quantity == 387

    assert (
        herbs.resource_type
        == "resource"
    )

    assert (
        herbs.source_column
        == "Y"
    )


def test_component_and_resource_groups(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_name(
        "Opulent Decoction"
    )

    assert item is not None

    assert [
        ingredient.name
        for ingredient
        in item.components
    ] == [
        "Opulent Jewel",
        "Precious Shell",
    ]

    assert [
        ingredient.name
        for ingredient
        in item.raw_resources
    ] == [
        "Herbs",
        "Oil",
    ]


def test_missing_name_returns_none(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    assert (
        service.get_by_name(
            "Does Not Exist"
        )
        is None
    )


def test_canonical_apostrophe_name_lookup(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_name(
        "Ice Queen's Summer Hat"
    )

    assert item is not None

    assert (
        item.name
        == "Ice Queen's Summer Hat"
    )


def test_get_by_id(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    item = service.get_by_id(
        "herbal_medicine_"
        "opulent_decoction"
    )

    assert item is not None

    assert (
        item.name
        == "Opulent Decoction"
    )


def test_get_all(
    tmp_path,
):
    service = GameDataService(
        make_fixture(
            tmp_path
        )
    )

    items = service.get_all()

    assert len(items) == 2

    assert {
        item.name
        for item in items
    } == {
        "Opulent Decoction",
        "Ice Queen's Summer Hat",
    }


def test_reload_rebuilds_indexes(
    tmp_path,
):
    data_dir = make_fixture(
        tmp_path
    )

    service = GameDataService(
        data_dir
    )

    assert (
        service.get_by_name(
            "Opulent Decoction"
        )
        is not None
    )

    new_items = [
        {
            "item_id": (
                "new_item"
            ),
            "name": (
                "New Item"
            ),
            "item_type": (
                "Sword"
            ),
            "tier": 1,
            "craft_time_seconds": 15,
            "base_value": 10,
            "required_workers": [],
        }
    ]

    new_recipes = [
        {
            "item_id": (
                "new_item"
            ),
            "ingredients": [],
        }
    ]

    write_data(
        data_dir,
        items=new_items,
        recipes=new_recipes,
    )

    service.reload()

    assert (
        service.get_by_name(
            "Opulent Decoction"
        )
        is None
    )

    assert (
        service.get_by_id(
            "herbal_medicine_"
            "opulent_decoction"
        )
        is None
    )

    assert (
        service.get_by_name(
            "New Item"
        )
        is not None
    )