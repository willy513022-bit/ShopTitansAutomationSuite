import re
import unicodedata
from typing import Any

from services.resource_column_map import RESOURCE_COLUMN_MAP


class BlueprintParser:
    COMPONENT_GROUPS = (
        (37, 38, 39),
        (40, 41, 42),
    )

    WORKER_GROUPS = (
        (17, 18),
        (19, 20),
        (21, 22),
    )

    RAW_RESOURCE_START_INDEX = 24
    RAW_RESOURCE_END_INDEX = 36

    def parse(
        self,
        rows: list[tuple[Any, ...]],
    ) -> list[dict[str, Any]]:
        if not rows:
            return []

        headers = rows[0]
        header_map = self._build_header_map(headers)
        blueprints: list[dict[str, Any]] = []

        for excel_row, row in enumerate(
            rows[1:],
            start=2,
        ):
            name = self._get(
                row,
                header_map,
                "Name",
            )

            item_type = self._get(
                row,
                header_map,
                "Type",
            )

            tier = self._get(
                row,
                header_map,
                "Tier",
            )

            if self._is_empty(name):
                continue

            if self._is_empty(item_type):
                continue

            if not isinstance(
                tier,
                (int, float),
            ):
                continue

            name_text = str(name).strip()
            item_type_text = str(item_type).strip()

            blueprints.append(
                {
                    "item_id": self._make_item_id(
                        item_type=item_type_text,
                        name=name_text,
                    ),
                    "name": name_text,
                    "item_type": item_type_text,
                    "tier": int(float(tier)),
                    "value": self._int_value(
                        self._get(
                            row,
                            header_map,
                            "Value",
                        )
                    ),
                    "craft_time_seconds": self._int_value(
                        self._get(
                            row,
                            header_map,
                            "Crafting Time (seconds)",
                        )
                    ),
                    "craft_time_formatted": self._clean_optional(
                        self._get(
                            row,
                            header_map,
                            "Crafting Time (formatted)",
                        )
                    ),
                    "merchant_xp": self._int_value(
                        self._get(
                            row,
                            header_map,
                            "Merchant XP",
                        )
                    ),
                    "worker_xp": self._int_value(
                        self._get(
                            row,
                            header_map,
                            "Worker XP",
                        )
                    ),
                    "required_workers": self._parse_workers(
                        row
                    ),
                    "components": self._parse_components(
                        row
                    ),
                    "raw_resources": self._parse_raw_resources(
                        row
                    ),
                    "_excel_row": excel_row,
                }
            )

        return blueprints

    def build_items(
        self,
        blueprints: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            {
                "item_id": row["item_id"],
                "name": row["name"],
                "item_type": row["item_type"],
                "tier": row["tier"],
                "craft_time_seconds": row[
                    "craft_time_seconds"
                ],
                "base_value": row["value"],
                "required_workers": row[
                    "required_workers"
                ],
            }
            for row in blueprints
        ]

    def build_recipes(
        self,
        blueprints: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        name_to_id = {
            row["name"]: row["item_id"]
            for row in blueprints
        }

        recipes: list[dict[str, Any]] = []

        for blueprint in blueprints:
            ingredients: list[dict[str, Any]] = []

            for component in blueprint["components"]:
                component_id = name_to_id.get(
                    component["name"]
                )

                ingredients.append(
                    {
                        "item_id": component_id,
                        "name": component["name"],
                        "quantity": component[
                            "quantity"
                        ],
                        "quality": component[
                            "quality"
                        ],
                        "resource_type": (
                            "item"
                            if component_id
                            else "quest_component"
                        ),
                    }
                )

            for column, quantity in blueprint[
                "raw_resources"
            ].items():
                resource_name = RESOURCE_COLUMN_MAP.get(
                    column,
                    f"raw_resource_{column}",
                )

                ingredients.append(
                    {
                        "item_id": None,
                        "name": resource_name,
                        "quantity": quantity,
                        "quality": None,
                        "resource_type": "resource",
                        "source_column": column,
                    }
                )

            recipes.append(
                {
                    "item_id": blueprint[
                        "item_id"
                    ],
                    "ingredients": ingredients,
                }
            )

        return recipes

    def _parse_workers(
        self,
        row: tuple[Any, ...],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for worker_index, level_index in (
            self.WORKER_GROUPS
        ):
            worker = self._row_value(
                row,
                worker_index,
            )

            if self._is_empty(worker):
                continue

            results.append(
                {
                    "worker": str(worker).strip(),
                    "level": self._int_value(
                        self._row_value(
                            row,
                            level_index,
                        )
                    ),
                }
            )

        return results

    def _parse_components(
        self,
        row: tuple[Any, ...],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for (
            name_index,
            quality_index,
            amount_index,
        ) in self.COMPONENT_GROUPS:
            name = self._row_value(
                row,
                name_index,
            )

            amount = self._row_value(
                row,
                amount_index,
            )

            if self._is_empty(name):
                continue

            if self._is_empty(amount):
                continue

            results.append(
                {
                    "name": str(name).strip(),
                    "quality": self._clean_optional(
                        self._row_value(
                            row,
                            quality_index,
                        )
                    ),
                    "quantity": self._int_value(
                        amount
                    ),
                }
            )

        return results

    def _parse_raw_resources(
        self,
        row: tuple[Any, ...],
    ) -> dict[str, int]:
        result: dict[str, int] = {}

        for index in range(
            self.RAW_RESOURCE_START_INDEX,
            self.RAW_RESOURCE_END_INDEX,
        ):
            value = self._row_value(
                row,
                index,
            )

            if self._is_empty(value):
                continue

            column = self._excel_column_name(
                index + 1
            )

            result[column] = self._int_value(
                value
            )

        return result

    @staticmethod
    def _build_header_map(
        headers: tuple[Any, ...],
    ) -> dict[str, list[int]]:
        result: dict[str, list[int]] = {}

        for index, value in enumerate(
            headers
        ):
            if value is None:
                continue

            key = str(value).strip()

            result.setdefault(
                key,
                [],
            ).append(index)

        return result

    @staticmethod
    def _get(
        row: tuple[Any, ...],
        header_map: dict[str, list[int]],
        header: str,
        occurrence: int = 0,
    ) -> Any:
        indexes = header_map.get(
            header,
            [],
        )

        if occurrence >= len(indexes):
            return None

        return BlueprintParser._row_value(
            row,
            indexes[occurrence],
        )

    @staticmethod
    def _row_value(
        row: tuple[Any, ...],
        index: int,
    ) -> Any:
        if index < 0:
            return None

        if index >= len(row):
            return None

        return row[index]

    @staticmethod
    def _is_empty(
        value: Any,
    ) -> bool:
        if value is None:
            return True

        if isinstance(value, str):
            return value.strip() in {
                "",
                "---",
            }

        return False

    @staticmethod
    def _clean_optional(
        value: Any,
    ) -> Any:
        if BlueprintParser._is_empty(value):
            return None

        return value

    @staticmethod
    def _int_value(
        value: Any,
    ) -> int:
        if BlueprintParser._is_empty(value):
            return 0

        try:
            return int(float(value))

        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _make_item_id(
        item_type: str,
        name: str,
    ) -> str:
        return BlueprintParser._slugify(
            f"{item_type}_{name}"
        )

    @staticmethod
    def _slugify(
        value: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFKD",
            value,
        )

        ascii_text = (
            normalized
            .encode(
                "ascii",
                "ignore",
            )
            .decode(
                "ascii"
            )
            .lower()
        )

        ascii_text = re.sub(
            r"[^a-z0-9]+",
            "_",
            ascii_text,
        )

        return ascii_text.strip("_")

    @staticmethod
    def _excel_column_name(
        number: int,
    ) -> str:
        result = ""

        while number:
            number, remainder = divmod(
                number - 1,
                26,
            )

            result = (
                chr(65 + remainder)
                + result
            )

        return result
