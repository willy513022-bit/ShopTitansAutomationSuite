from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from vision_core.roi import ROI


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DEFAULT_CONFIG_PATH = (
    PROJECT_ROOT
    / "data"
    / "config"
    / "vision_rois.json"
)


class ROIStore:
    def __init__(
        self,
        path: str | Path = DEFAULT_CONFIG_PATH,
    ) -> None:
        self.path = Path(path)

    def load_all(self) -> dict[str, ROI]:
        if not self.path.exists():
            return {}

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        return {
            name: ROI(
                name=name,
                x=int(values["x"]),
                y=int(values["y"]),
                width=int(values["width"]),
                height=int(values["height"]),
            )
            for name, values in payload.items()
        }

    def get(
        self,
        name: str,
    ) -> ROI | None:
        return self.load_all().get(name)

    def save(
        self,
        roi: ROI,
    ) -> None:
        all_rois = self.load_all()
        all_rois[roi.name] = roi

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            name: {
                key: value
                for key, value in asdict(value).items()
                if key != "name"
            }
            for name, value in all_rois.items()
        }

        temporary = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        with temporary.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=2,
            )

        temporary.replace(self.path)
