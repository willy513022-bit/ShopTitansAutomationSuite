from pathlib import Path


TARGET_PATH = Path(
    "services/official_data_importer.py"
)

MARKER = "    @staticmethod\n    def _json_safe("


NEW_TAIL = '''    @staticmethod
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
'''


def main() -> None:
    if not TARGET_PATH.exists():
        print(
            "找不到檔案：",
            TARGET_PATH.resolve(),
        )
        return

    source = TARGET_PATH.read_text(
        encoding="utf-8",
    )

    # 確保 import 包含 timedelta。
    old_import = (
        "from datetime import "
        "date, datetime, time"
    )

    new_import = (
        "from datetime import "
        "date, datetime, time, timedelta"
    )

    if new_import not in source:
        source = source.replace(
            old_import,
            new_import,
            1,
        )

    # 同時支援 Windows CRLF。
    normalized = source.replace(
        "\r\n",
        "\n",
    )

    marker_position = normalized.find(
        MARKER
    )

    if marker_position < 0:
        print(
            "找不到 _json_safe()，"
            "沒有修改檔案。"
        )
        return

    backup_path = TARGET_PATH.with_suffix(
        ".py.backup"
    )

    backup_path.write_text(
        source,
        encoding="utf-8",
    )

    repaired = (
        normalized[:marker_position]
        + NEW_TAIL
    )

    TARGET_PATH.write_text(
        repaired,
        encoding="utf-8",
    )

    print("修復完成")
    print("檔案：", TARGET_PATH.resolve())
    print("備份：", backup_path.resolve())


if __name__ == "__main__":
    main()