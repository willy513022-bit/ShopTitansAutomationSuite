from __future__ import annotations

import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SOURCE_PATH = Path(
    r"C:\PythonProject\ShopTitansAutomationSuite"
    r"\data\database\shop_titans_data.xlsx"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "data"
    / "official_database"
)

RAW_SHEETS_DIRECTORY = (
    OUTPUT_ROOT
    / "raw_sheets"
)

NORMALIZED_DIRECTORY = (
    OUTPUT_ROOT
    / "normalized"
)

BACKUP_DIRECTORY = (
    OUTPUT_ROOT
    / "backups"
)


@dataclass(frozen=True)
class ImportSummary:
    source_path: str
    sheet_count: int
    blueprint_count: int
    worker_count: int
    quest_component_count: int
    output_directory: str


class OfficialDataImporter:
    """
    將官方 Shop Titans Data Spreadsheet 轉換成 JSON。

    會輸出兩種資料：

    1. raw_sheets
       每張 Excel 工作表完整轉成 JSON。
       不丟棄尚未標準化的欄位。

    2. normalized
       專案目前會直接使用的結構化資料：
       - blueprints.json
       - items.json
       - recipes.json
       - workers.json
       - quest_components.json
       - metadata.json
    """

    BLUEPRINT_SHEET = "Blueprints"
    WORKER_SHEET = "Workers"
    QUEST_COMPONENT_SHEET = "Quest Components"
    CHANGELOG_SHEET = "Changelog"

    EMPTY_VALUES = {
        None,
        "",
        "---",
    }

    def __init__(
        self,
        source_path: Path | str = DEFAULT_SOURCE_PATH,
        output_root: Path = OUTPUT_ROOT,
    ) -> None:
        self.source_path = Path(source_path)

        self.output_root = output_root

        self.raw_sheets_directory = (
            output_root
            / "raw_sheets"
        )

        self.normalized_directory = (
            output_root
            / "normalized"
        )

        self.backup_directory = (
            output_root
            / "backups"
        )

    def run(self) -> ImportSummary:
        self._validate_source()

        self._prepare_directories()

        workbook = load_workbook(
            self.source_path,
            read_only=True,
            data_only=True,
        )

        self._backup_existing_normalized_data()

        self._export_all_raw_sheets(
            workbook
        )

        blueprints = self._parse_blueprints(
            workbook[self.BLUEPRINT_SHEET]
        )

        workers = self._parse_workers(
            workbook[self.WORKER_SHEET]
        )

        quest_components = (
            self._parse_quest_components(
                workbook[
                    self.QUEST_COMPONENT_SHEET
                ]
            )
        )

        items = self._build_items(
            blueprints
        )

        recipes = self._build_recipes(
            blueprints
        )

        metadata = self._build_metadata(
            workbook=workbook,
            blueprint_count=len(
                blueprints
            ),
        )

        self._write_json(
            self.normalized_directory
            / "blueprints.json",
            blueprints,
        )

        self._write_json(
            self.normalized_directory
            / "items.json",
            items,
        )

        self._write_json(
            self.normalized_directory
            / "recipes.json",
            recipes,
        )

        self._write_json(
            self.normalized_directory
            / "workers.json",
            workers,
        )

        self._write_json(
            self.normalized_directory
            / "quest_components.json",
            quest_components,
        )

        self._write_json(
            self.normalized_directory
            / "metadata.json",
            metadata,
        )

        self._copy_for_game_data_v2(
            items=items,
            recipes=recipes,
        )

        return ImportSummary(
            source_path=str(
                self.source_path
            ),
            sheet_count=len(
                workbook.sheetnames
            ),
            blueprint_count=len(
                blueprints
            ),
            worker_count=len(
                workers
            ),
            quest_component_count=len(
                quest_components
            ),
            output_directory=str(
                self.output_root
            ),
        )

    def _validate_source(self) -> None:
        if not self.source_path.exists():
            raise FileNotFoundError(
                "找不到官方資料表："
                f"{self.source_path}"
            )

        if (
            self.source_path.suffix.lower()
            != ".xlsx"
        ):
            raise ValueError(
                "來源檔案必須是 .xlsx"
            )

    def _prepare_directories(
        self,
    ) -> None:
        self.raw_sheets_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.normalized_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.backup_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _backup_existing_normalized_data(
        self,
    ) -> None:
        if not (
            self.normalized_directory.exists()
        ):
            return

        existing_files = list(
            self.normalized_directory.glob(
                "*.json"
            )
        )

        if not existing_files:
            return

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        destination = (
            self.backup_directory
            / timestamp
        )

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        for file_path in existing_files:
            shutil.copy2(
                file_path,
                destination
                / file_path.name,
            )

    def _export_all_raw_sheets(
        self,
        workbook,
    ) -> None:
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[
                sheet_name
            ]

            rows = list(
                worksheet.iter_rows(
                    values_only=True
                )
            )

            if not rows:
                payload = {
                    "sheet_name": sheet_name,
                    "headers": [],
                    "rows": [],
                }

            else:
                headers = (
                    self._build_unique_headers(
                        rows[0]
                    )
                )

                converted_rows = []

                for row_number, row in enumerate(
                    rows[1:],
                    start=2,
                ):
                    if self._is_empty_row(
                        row
                    ):
                        continue

                    record = {
                        "_excel_row": (
                            row_number
                        )
                    }

                    for column_index, (
                        header,
                        value,
                    ) in enumerate(
                        zip(
                            headers,
                            row,
                            strict=False,
                        ),
                        start=1,
                    ):
                        record[header] = (
                            self._json_safe(
                                value
                            )
                        )

                    converted_rows.append(
                        record
                    )

                payload = {
                    "sheet_name": sheet_name,
                    "headers": headers,
                    "rows": converted_rows,
                }

            filename = (
                self._slugify(
                    sheet_name
                )
                + ".json"
            )

            self._write_json(
                self.raw_sheets_directory
                / filename,
                payload,
            )

    def _parse_blueprints(
        self,
        worksheet,
    ) -> list[dict[str, Any]]:
        rows = worksheet.iter_rows(
            values_only=True
        )

        try:
            headers = next(rows)
        except StopIteration:
            return []

        header_map = (
            self._build_header_index_map(
                headers
            )
        )

        blueprints: list[
            dict[str, Any]
        ] = []

        for excel_row, row in enumerate(
            rows,
            start=2,
        ):
            name = self._get_by_header(
                row,
                header_map,
                "Name",
            )

            item_type = self._get_by_header(
                row,
                header_map,
                "Type",
            )

            tier = self._get_by_header(
                row,
                header_map,
                "Tier",
            )

            if (
                self._is_empty_value(name)
                or self._is_empty_value(
                    item_type
                )
                or not isinstance(
                    tier,
                    (int, float),
                )
            ):
                continue

            name_text = str(
                name
            ).strip()

            item_id = self._make_item_id(
                name=name_text,
                item_type=str(
                    item_type
                ),
            )

            workers = (
                self._extract_worker_requirements(
                    row
                )
            )

            components = (
                self._extract_components(
                    row
                )
            )

            raw_resources = (
                self._extract_raw_resource_columns(
                    row
                )
            )

            blueprint = {
                "item_id": item_id,
                "name": name_text,
                "type": str(
                    item_type
                ).strip(),
                "tier": int(
                    float(tier)
                ),
                "unlock_prerequisite": (
                    self._clean_optional(
                        self._get_by_header(
                            row,
                            header_map,
                            "Unlock Prerequisite",
                        )
                    )
                ),
                "research_scrolls": (
                    self._number_or_none(
                        self._get_by_header(
                            row,
                            header_map,
                            "Research Scrolls",
                        )
                    )
                ),
                "antique_tokens": (
                    self._number_or_none(
                        self._get_by_header(
                            row,
                            header_map,
                            "Antique Tokens",
                        )
                    )
                ),
                "value": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Value",
                        )
                    )
                ),
                "craft_time_seconds": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Crafting Time (seconds)",
                        )
                    )
                ),
                "craft_time_formatted": (
                    self._clean_optional(
                        self._get_by_header(
                            row,
                            header_map,
                            "Crafting Time (formatted)",
                        )
                    )
                ),
                "merchant_xp": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Merchant XP",
                        )
                    )
                ),
                "worker_xp": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Worker XP",
                        )
                    )
                ),
                "fusion_xp": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Fusion XP",
                        )
                    )
                ),
                "favor": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Favor",
                        )
                    )
                ),
                "airship_power": (
                    self._int_or_zero(
                        self._get_by_header(
                            row,
                            header_map,
                            "Airship Power",
                        )
                    )
                ),
                "workers": workers,
                "components": components,
                "raw_resources": (
                    raw_resources
                ),
                "_excel_row": excel_row,
            }

            blueprints.append(
                blueprint
            )

        return blueprints

    def _extract_worker_requirements(
        self,
        row: tuple[Any, ...],
    ) -> list[dict[str, Any]]:
        # Excel 欄位：
        # R/S、T/U、V/W
        worker_pairs = (
            (17, 18),
            (19, 20),
            (21, 22),
        )

        requirements = []

        for worker_index, level_index in (
            worker_pairs
        ):
            worker = self._row_value(
                row,
                worker_index,
            )

            level = self._row_value(
                row,
                level_index,
            )

            if self._is_empty_value(
                worker
            ):
                continue

            requirements.append(
                {
                    "worker": str(
                        worker
                    ).strip(),
                    "level": (
                        self._int_or_zero(
                            level
                        )
                    ),
                }
            )

        return requirements

    def _extract_components(
        self,
        row: tuple[Any, ...],
    ) -> list[dict[str, Any]]:
        # Blueprints 工作表：
        # AL/AM/AN 及 AO/AP/AQ
        component_groups = (
            (37, 38, 39),
            (40, 41, 42),
        )

        components = []

        for (
            name_index,
            quality_index,
            amount_index,
        ) in component_groups:
            name = self._row_value(
                row,
                name_index,
            )

            amount = self._row_value(
                row,
                amount_index,
            )

            if (
                self._is_empty_value(name)
                or self._is_empty_value(
                    amount
                )
            ):
                continue

            components.append(
                {
                    "name": str(
                        name
                    ).strip(),
                    "quality": (
                        self._clean_optional(
                            self._row_value(
                                row,
                                quality_index,
                            )
                        )
                    ),
                    "quantity": (
                        self._int_or_zero(
                            amount
                        )
                    ),
                }
            )

        return components

    def _extract_raw_resource_columns(
        self,
        row: tuple[Any, ...],
    ) -> dict[str, Any]:
        """
        Blueprints 的 Y:AK 是資源欄位，但第一列標題為空，
        因此先保留欄位位置與原始值。

        下一階段再依工作表格式／Legend Key
        對應成 Iron、Wood、Steel、Herbs 等名稱。
        """

        result: dict[str, Any] = {}

        for zero_based_index in range(
            24,
            36,
        ):
            value = self._row_value(
                row,
                zero_based_index,
            )

            if self._is_empty_value(
                value
            ):
                continue

            excel_column = (
                self._excel_column_name(
                    zero_based_index + 1
                )
            )

            result[
                excel_column
            ] = self._json_safe(
                value
            )

        return result

    def _build_items(
        self,
        blueprints: list[
            dict[str, Any]
        ],
    ) -> list[dict[str, Any]]:
        return [
            {
                "item_id": (
                    blueprint[
                        "item_id"
                    ]
                ),
                "name": (
                    blueprint["name"]
                ),
                "item_type": (
                    blueprint["type"]
                ),
                "tier": (
                    blueprint["tier"]
                ),
                "craft_time_seconds": (
                    blueprint[
                        "craft_time_seconds"
                    ]
                ),
                "base_value": (
                    blueprint["value"]
                ),
                "required_workers": (
                    blueprint[
                        "workers"
                    ]
                ),
            }
            for blueprint in blueprints
        ]

    def _build_recipes(
        self,
        blueprints: list[
            dict[str, Any]
        ],
    ) -> list[dict[str, Any]]:
        name_to_id = {
            blueprint["name"]: (
                blueprint[
                    "item_id"
                ]
            )
            for blueprint in blueprints
        }

        recipes = []

        for blueprint in blueprints:
            ingredients = []

            for component in (
                blueprint["components"]
            ):
                component_name = (
                    component["name"]
                )

                component_item_id = (
                    name_to_id.get(
                        component_name
                    )
                )

                ingredients.append(
                    {
                        "item_id": (
                            component_item_id
                        ),
                        "name": (
                            component_name
                        ),
                        "quantity": (
                            component[
                                "quantity"
                            ]
                        ),
                        "quality": (
                            component[
                                "quality"
                            ]
                        ),
                        "resource_type": (
                            "item"
                            if component_item_id
                            else "quest_component"
                        ),
                    }
                )

            # 未命名的基礎資源先完整保留。
            for column_name, value in (
                blueprint[
                    "raw_resources"
                ].items()
            ):
                ingredients.append(
                    {
                        "item_id": None,
                        "name": (
                            f"raw_resource_"
                            f"{column_name}"
                        ),
                        "quantity": value,
                        "quality": None,
                        "resource_type": (
                            "raw_resource"
                        ),
                        "source_column": (
                            column_name
                        ),
                    }
                )

            recipes.append(
                {
                    "item_id": (
                        blueprint[
                            "item_id"
                        ]
                    ),
                    "ingredients": (
                        ingredients
                    ),
                }
            )

        return recipes

    def _parse_workers(
        self,
        worksheet,
    ) -> list[dict[str, Any]]:
        rows = worksheet.iter_rows(
            values_only=True
        )

        try:
            headers = next(rows)
        except StopIteration:
            return []

        header_map = (
            self._build_header_index_map(
                headers
            )
        )

        workers = []

        for excel_row, row in enumerate(
            rows,
            start=2,
        ):
            worker = self._get_by_header(
                row,
                header_map,
                "Worker",
            )

            name = self._get_by_header(
                row,
                header_map,
                "Name",
            )

            if (
                self._is_empty_value(
                    worker
                )
                or self._is_empty_value(
                    name
                )
            ):
                continue

            unlocks_raw = self._get_by_header(
                row,
                header_map,
                "Blueprint Unlocks",
            )

            unlocks = []

            if not self._is_empty_value(
                unlocks_raw
            ):
                unlocks = [
                    value.strip()
                    for value in str(
                        unlocks_raw
                    ).split(",")
                    if value.strip()
                ]

            workers.append(
                {
                    "worker_id": (
                        self._slugify(
                            str(worker)
                        )
                    ),
                    "worker": str(
                        worker
                    ).strip(),
                    "name": str(
                        name
                    ).strip(),
                    "level_required": (
                        self._number_or_none(
                            self._get_by_header(
                                row,
                                header_map,
                                "Level Required",
                            )
                        )
                    ),
                    "building_prerequisite": (
                        self._clean_optional(
                            self._get_by_header(
                                row,
                                header_map,
                                "Building Prerequisite",
                            )
                        )
                    ),
                    "gold_cost": (
                        self._number_or_none(
                            self._get_by_header(
                                row,
                                header_map,
                                "Gold Cost",
                            )
                        )
                    ),
                    "gem_cost": (
                        self._number_or_none(
                            self._get_by_header(
                                row,
                                header_map,
                                "Gem Cost",
                            )
                        )
                    ),
                    "blueprint_unlocks": (
                        unlocks
                    ),
                    "_excel_row": (
                        excel_row
                    ),
                }
            )

        return workers

    def _parse_quest_components(
        self,
        worksheet,
    ) -> list[dict[str, Any]]:
        rows = worksheet.iter_rows(
            values_only=True
        )

        try:
            headers = next(rows)
        except StopIteration:
            return []

        header_map = (
            self._build_header_index_map(
                headers
            )
        )

        components = []

        for excel_row, row in enumerate(
            rows,
            start=2,
        ):
            name = self._get_by_header(
                row,
                header_map,
                "Name",
            )

            tier = self._get_by_header(
                row,
                header_map,
                "Tier",
            )

            if self._is_empty_value(
                name
            ):
                continue

            components.append(
                {
                    "component_id": (
                        self._slugify(
                            str(name)
                        )
                    ),
                    "name": str(
                        name
                    ).strip(),
                    "type": (
                        self._clean_optional(
                            self._get_by_header(
                                row,
                                header_map,
                                "Type",
                            )
                        )
                    ),
                    "tier": (
                        self._int_or_zero(
                            tier
                        )
                    ),
                    "value": (
                        self._int_or_zero(
                            self._get_by_header(
                                row,
                                header_map,
                                "Value",
                            )
                        )
                    ),
                    "quest_area": (
                        self._clean_optional(
                            self._get_by_header(
                                row,
                                header_map,
                                "Quest Area",
                            )
                        )
                    ),
                    "_excel_row": (
                        excel_row
                    ),
                }
            )

        return components

    def _build_metadata(
        self,
        workbook,
        blueprint_count: int,
    ) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "source_file": str(
                self.source_path
            ),
            "source_filename": (
                self.source_path.name
            ),
            "imported_at": (
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )
            ),
            "sheet_names": (
                workbook.sheetnames
            ),
            "sheet_count": len(
                workbook.sheetnames
            ),
            "blueprint_count": (
                blueprint_count
            ),
            "notes": [
                (
                    "raw_sheets 保留完整原始工作表資料。"
                ),
                (
                    "normalized 提供目前 V2 "
                    "程式直接使用的資料。"
                ),
                (
                    "Blueprints Y:AK 的資源欄位"
                    "因第一列表頭為空，目前先以"
                    " raw_resource_欄號 保存。"
                ),
            ],
        }

    def _copy_for_game_data_v2(
        self,
        items: list[dict[str, Any]],
        recipes: list[dict[str, Any]],
    ) -> None:
        game_data_directory = (
            PROJECT_ROOT
            / "data"
            / "game_data"
        )

        game_data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._write_json(
            game_data_directory
            / "items.json",
            items,
        )

        self._write_json(
            game_data_directory
            / "recipes.json",
            recipes,
        )

        self._write_json(
            game_data_directory
            / "meta.json",
            {
                "schema_version": 2,
                "source": str(
                    self.source_path
                ),
                "updated_at": (
                    datetime.now()
                    .isoformat(
                        timespec="seconds"
                    )
                ),
                "item_count": len(
                    items
                ),
                "recipe_count": len(
                    recipes
                ),
            },
        )

    @staticmethod
    def _build_unique_headers(
        row: tuple[Any, ...],
    ) -> list[str]:
        headers = []
        used: dict[str, int] = {}

        for column_number, value in enumerate(
            row,
            start=1,
        ):
            if value is None:
                base = (
                    f"column_"
                    f"{column_number:03d}"
                )
            else:
                base = str(
                    value
                ).strip()

                if not base:
                    base = (
                        f"column_"
                        f"{column_number:03d}"
                    )

            count = used.get(
                base,
                0,
            )

            used[base] = count + 1

            if count:
                header = (
                    f"{base}__"
                    f"{count + 1}"
                )
            else:
                header = base

            headers.append(
                header
            )

        return headers

    @staticmethod
    def _build_header_index_map(
        headers: tuple[Any, ...],
    ) -> dict[str, list[int]]:
        result: dict[
            str,
            list[int],
        ] = {}

        for index, value in enumerate(
            headers
        ):
            if value is None:
                continue

            key = str(
                value
            ).strip()

            result.setdefault(
                key,
                [],
            ).append(
                index
            )

        return result

    @staticmethod
    def _get_by_header(
        row: tuple[Any, ...],
        header_map: dict[
            str,
            list[int],
        ],
        header: str,
        occurrence: int = 0,
    ) -> Any:
        indexes = header_map.get(
            header,
            [],
        )

        if occurrence >= len(
            indexes
        ):
            return None

        index = indexes[
            occurrence
        ]

        return OfficialDataImporter._row_value(
            row,
            index,
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

    @classmethod
    def _is_empty_value(
        cls,
        value: Any,
    ) -> bool:
        if value in cls.EMPTY_VALUES:
            return True

        if isinstance(
            value,
            str,
        ):
            return (
                value.strip()
                in cls.EMPTY_VALUES
            )

        return False

    @classmethod
    def _is_empty_row(
        cls,
        row: tuple[Any, ...],
    ) -> bool:
        return all(
            cls._is_empty_value(
                value
            )
            for value in row
        )

    @classmethod
    def _clean_optional(
        cls,
        value: Any,
    ) -> Any:
        if cls._is_empty_value(
            value
        ):
            return None

        return cls._json_safe(
            value
        )

    @classmethod
    def _number_or_none(
        cls,
        value: Any,
    ) -> int | float | None:
        if cls._is_empty_value(
            value
        ):
            return None

        if isinstance(
            value,
            bool,
        ):
            return int(value)

        if isinstance(
            value,
            int,
        ):
            return value

        if isinstance(
            value,
            float,
        ):
            if value.is_integer():
                return int(value)

            return value

        try:
            converted = float(
                str(value)
            )

            if converted.is_integer():
                return int(
                    converted
                )

            return converted

        except (
            TypeError,
            ValueError,
        ):
            return None

    @classmethod
    def _int_or_zero(
        cls,
        value: Any,
    ) -> int:
        number = cls._number_or_none(
            value
        )

        if number is None:
            return 0

        return int(number)

    @staticmethod
    def _make_item_id(
        name: str,
        item_type: str,
    ) -> str:
        return (
            OfficialDataImporter
            ._slugify(
                f"{item_type}_{name}"
            )
        )

    @staticmethod
    def _slugify(
        value: str,
    ) -> str:
        normalized = (
            unicodedata.normalize(
                "NFKD",
                value,
            )
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
        )

        ascii_text = (
            ascii_text.lower()
        )

        ascii_text = re.sub(
            r"[^a-z0-9]+",
            "_",
            ascii_text,
        )

        return ascii_text.strip(
            "_"
        )

    @staticmethod
    def _excel_column_name(
        column_number: int,
    ) -> str:
        name = ""

        while column_number:
            column_number, remainder = divmod(
                column_number - 1,
                26,
            )

            name = (
                chr(
                    65 + remainder
                )
                + name
            )

        return name

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat(
                timespec="seconds"
            )

        if isinstance(
            value,
            date,
        ):
            return value.isoformat()

        if isinstance(
            value,
            time,
        ):
            return value.isoformat()

        if isinstance(
            value,
            timedelta,
        ):
            total_seconds = int(
                value.total_seconds()
            )

            hours, remainder = divmod(
                total_seconds,
                3600,
            )

            minutes, seconds = divmod(
                remainder,
                60,
            )

            return {
                "total_seconds": total_seconds,
                "formatted": (
                    f"{hours:02d}:"
                    f"{minutes:02d}:"
                    f"{seconds:02d}"
                ),
            }

        if isinstance(
            value,
            float,
        ):
            if value.is_integer():
                return int(value)

        return value

    @staticmethod
    def _write_json(
        path: Path,
        data: Any,
    ) -> None:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = path.with_suffix(
            path.suffix + ".tmp"
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        temporary_path.replace(
            path
        )