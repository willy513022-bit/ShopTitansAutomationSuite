from __future__ import annotations

import json
from pathlib import Path

from models.game_item import (
    GameItem,
    RecipeIngredient,
    WorkerRequirement,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

GAME_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "game_data"
)


class GameDataService:
    def __init__(
        self,
        data_directory: (
            str
            | Path
            | None
        ) = None,
    ) -> None:
        self._data_directory = (
            Path(data_directory)
            if data_directory
            is not None
            else GAME_DATA_DIR
        )

        self._items_by_id: dict[
            str,
            GameItem,
        ] = {}

        self._items_by_name: dict[
            str,
            GameItem,
        ] = {}

        self.reload()

    @property
    def data_directory(
        self,
    ) -> Path:
        return self._data_directory

    def reload(
        self,
    ) -> None:
        item_rows = self._load_json(
            "items.json"
        )

        recipe_rows = self._load_json(
            "recipes.json"
        )

        recipes_by_id = (
            self._build_recipe_map(
                recipe_rows
            )
        )

        items = tuple(
            self._build_item(
                row=row,
                ingredients=(
                    recipes_by_id.get(
                        str(
                            row["item_id"]
                        ),
                        (),
                    )
                ),
            )
            for row in item_rows
        )

        # 每次 reload 都完整重建索引，
        # 不保留舊資料。
        self._items_by_id = {
            item.item_id: item
            for item in items
        }

        self._items_by_name = {
            item.name: item
            for item in items
        }

    def get_all(
        self,
    ) -> list[GameItem]:
        return list(
            self._items_by_id.values()
        )

    def get_by_id(
        self,
        item_id: str,
    ) -> GameItem | None:
        return self._items_by_id.get(
            item_id
        )

    def get_by_name(
        self,
        name: str,
    ) -> GameItem | None:
        return self._items_by_name.get(
            name
        )

    def _load_json(
        self,
        filename: str,
    ) -> list[dict]:
        path = (
            self._data_directory
            / filename
        )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

        if not isinstance(
            data,
            list,
        ):
            raise ValueError(
                f"{filename} must contain a JSON list"
            )

        return data

    @staticmethod
    def _build_recipe_map(
        recipe_rows: list[dict],
    ) -> dict[
        str,
        tuple[
            RecipeIngredient,
            ...
        ],
    ]:
        result: dict[
            str,
            tuple[
                RecipeIngredient,
                ...
            ],
        ] = {}

        for row in recipe_rows:
            item_id = str(
                row["item_id"]
            )

            ingredients = tuple(
                GameDataService
                ._build_ingredient(
                    ingredient
                )
                for ingredient
                in row.get(
                    "ingredients",
                    [],
                )
            )

            result[
                item_id
            ] = ingredients

        return result

    @staticmethod
    def _build_ingredient(
        row: dict,
    ) -> RecipeIngredient:
        item_id = row.get(
            "item_id"
        )

        if item_id is not None:
            item_id = str(
                item_id
            )

        quality = row.get(
            "quality"
        )

        source_column = row.get(
            "source_column"
        )

        return RecipeIngredient(
            item_id=item_id,
            name=str(
                row["name"]
            ),
            quantity=int(
                row["quantity"]
            ),
            resource_type=str(
                row.get(
                    "resource_type",
                    "item",
                )
            ),
            quality=(
                str(quality)
                if quality is not None
                else None
            ),
            source_column=(
                str(source_column)
                if source_column
                is not None
                else None
            ),
        )

    @staticmethod
    def _build_worker(
        row: dict,
    ) -> WorkerRequirement:
        return WorkerRequirement(
            worker=str(
                row["worker"]
            ),
            level=int(
                row.get(
                    "level",
                    0,
                )
            ),
        )

    @staticmethod
    def _build_item(
        *,
        row: dict,
        ingredients: tuple[
            RecipeIngredient,
            ...
        ],
    ) -> GameItem:
        workers = tuple(
            GameDataService
            ._build_worker(
                worker
            )
            for worker
            in row.get(
                "required_workers",
                [],
            )
        )

        return GameItem(
            item_id=str(
                row["item_id"]
            ),
            name=str(
                row["name"]
            ),
            item_type=str(
                row.get(
                    "item_type",
                    "Unknown",
                )
            ),
            tier=int(
                row.get(
                    "tier",
                    0,
                )
            ),
            craft_time_seconds=int(
                row.get(
                    "craft_time_seconds",
                    0,
                )
            ),
            base_value=int(
                row.get(
                    "base_value",
                    0,
                )
            ),
            required_workers=workers,
            ingredients=ingredients,
        )


game_data_service = (
    GameDataService()
)