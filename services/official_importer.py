from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from services.blueprint_parser import (
    BlueprintParser,
)
from services.excel_reader import (
    ExcelReader,
)
from services.json_exporter import (
    JsonExporter,
)
from services.worker_parser import (
    WorkerParser,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DEFAULT_SOURCE = Path(
    r"C:\PythonProject"
    r"\ShopTitansAutomationSuite"
    r"\data\database"
    r"\shop_titans_data.xlsx"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "data"
    / "official_database"
)

GAME_DATA_ROOT = (
    PROJECT_ROOT
    / "data"
    / "game_data"
)


@dataclass(frozen=True)
class OfficialImportSummary:
    blueprint_count: int
    item_count: int
    recipe_count: int
    worker_count: int
    sheet_count: int
    output_directory: str


class OfficialImporter:
    def __init__(
        self,
        source_path: str | Path = (
            DEFAULT_SOURCE
        ),
    ) -> None:
        self.source_path = Path(
            source_path
        )

        self.reader = ExcelReader(
            self.source_path
        )

        self.blueprint_parser = (
            BlueprintParser()
        )

        self.worker_parser = (
            WorkerParser()
        )

        self.exporter = (
            JsonExporter()
        )

    def run(
        self,
    ) -> OfficialImportSummary:
        blueprint_rows = (
            self.reader.read_rows(
                "Blueprints"
            )
        )

        worker_rows = (
            self.reader.read_rows(
                "Workers"
            )
        )

        blueprints = (
            self.blueprint_parser.parse(
                blueprint_rows
            )
        )

        items = (
            self.blueprint_parser
            .build_items(
                blueprints
            )
        )

        recipes = (
            self.blueprint_parser
            .build_recipes(
                blueprints
            )
        )

        workers = (
            self.worker_parser.parse(
                worker_rows
            )
        )

        normalized_root = (
            OUTPUT_ROOT
            / "normalized"
        )

        self.exporter.write(
            normalized_root
            / "blueprints.json",
            blueprints,
        )

        self.exporter.write(
            normalized_root
            / "items.json",
            items,
        )

        self.exporter.write(
            normalized_root
            / "recipes.json",
            recipes,
        )

        self.exporter.write(
            normalized_root
            / "workers.json",
            workers,
        )

        metadata = {
            "schema_version": 2,
            "source_file": str(
                self.source_path
            ),
            "imported_at": (
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )
            ),
            "sheet_names": (
                self.reader.sheet_names()
            ),
            "sheet_count": len(
                self.reader.sheet_names()
            ),
            "blueprint_count": len(
                blueprints
            ),
            "worker_count": len(
                workers
            ),
        }

        self.exporter.write(
            normalized_root
            / "metadata.json",
            metadata,
        )

        self.exporter.write(
            GAME_DATA_ROOT
            / "items.json",
            items,
        )

        self.exporter.write(
            GAME_DATA_ROOT
            / "recipes.json",
            recipes,
        )

        self.exporter.write(
            GAME_DATA_ROOT
            / "meta.json",
            metadata,
        )

        return OfficialImportSummary(
            blueprint_count=len(
                blueprints
            ),
            item_count=len(items),
            recipe_count=len(
                recipes
            ),
            worker_count=len(
                workers
            ),
            sheet_count=len(
                self.reader.sheet_names()
            ),
            output_directory=str(
                normalized_root
            ),
        )