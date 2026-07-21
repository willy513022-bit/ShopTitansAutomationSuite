import json
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from pathlib import Path
from typing import Any


class JsonExporter:
    def write(
        self,
        path: str | Path,
        data: Any,
    ) -> None:
        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = (
            path.with_suffix(
                path.suffix + ".tmp"
            )
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
                default=self._json_default,
            )

        temporary_path.replace(
            path
        )

    @staticmethod
    def _json_default(
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

            return {
                "total_seconds": (
                    total_seconds
                ),
                "formatted": str(value),
            }

        raise TypeError(
            f"無法轉換成 JSON："
            f"{type(value).__name__}"
        )