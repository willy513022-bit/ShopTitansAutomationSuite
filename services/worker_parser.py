from typing import Any


class WorkerParser:
    def parse(
        self,
        rows: list[tuple[Any, ...]],
    ) -> list[dict]:
        if not rows:
            return []

        headers = rows[0]

        header_map = {
            str(value).strip(): index
            for index, value in enumerate(
                headers
            )
            if value is not None
        }

        workers = []

        for excel_row, row in enumerate(
            rows[1:],
            start=2,
        ):
            worker = self._get(
                row,
                header_map,
                "Worker",
            )

            name = self._get(
                row,
                header_map,
                "Name",
            )

            if not worker or not name:
                continue

            workers.append(
                {
                    "worker": str(
                        worker
                    ).strip(),
                    "name": str(
                        name
                    ).strip(),
                    "level_required": (
                        self._number(
                            self._get(
                                row,
                                header_map,
                                "Level Required",
                            )
                        )
                    ),
                    "building_prerequisite": (
                        self._optional(
                            self._get(
                                row,
                                header_map,
                                "Building Prerequisite",
                            )
                        )
                    ),
                    "gold_cost": self._number(
                        self._get(
                            row,
                            header_map,
                            "Gold Cost",
                        )
                    ),
                    "gem_cost": self._number(
                        self._get(
                            row,
                            header_map,
                            "Gem Cost",
                        )
                    ),
                    "blueprint_unlocks": (
                        self._split_list(
                            self._get(
                                row,
                                header_map,
                                "Blueprint Unlocks",
                            )
                        )
                    ),
                    "_excel_row": excel_row,
                }
            )

        return workers

    @staticmethod
    def _get(
        row,
        header_map,
        name,
    ):
        index = header_map.get(name)

        if index is None:
            return None

        if index >= len(row):
            return None

        return row[index]

    @staticmethod
    def _optional(value):
        if value in (
            None,
            "",
            "---",
        ):
            return None

        return value

    @staticmethod
    def _number(value):
        if value in (
            None,
            "",
            "---",
        ):
            return None

        try:
            number = float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

        if number.is_integer():
            return int(number)

        return number

    @staticmethod
    def _split_list(value):
        if value in (
            None,
            "",
            "---",
        ):
            return []

        return [
            part.strip()
            for part in str(value).split(",")
            if part.strip()
        ]