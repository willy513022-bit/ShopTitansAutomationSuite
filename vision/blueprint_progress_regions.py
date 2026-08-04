from __future__ import annotations

from dataclasses import dataclass

from vision.blueprint_progress_models import (
    ImageRegion,
)


@dataclass(frozen=True, slots=True)
class BlueprintProgressRegionConfig:
    """
    進度區相對於整張製作卡片的比例。

    預設值是第一版估計值，之後會依真實截圖微調。

    x_fraction:
        進度區左側位於卡片寬度的比例。

    y_fraction:
        進度區上側位於卡片高度的比例。

    width_fraction / height_fraction:
        進度區占卡片的大小比例。
    """

    x_fraction: float = 0.15
    y_fraction: float = 0.76
    width_fraction: float = 0.70
    height_fraction: float = 0.18

    def __post_init__(self) -> None:
        values = (
            self.x_fraction,
            self.y_fraction,
            self.width_fraction,
            self.height_fraction,
        )

        if any(
            value < 0.0 or value > 1.0
            for value in values
        ):
            raise ValueError(
                "region fractions must be between 0 and 1"
            )

        if self.width_fraction <= 0:
            raise ValueError(
                "width_fraction must be greater than 0"
            )

        if self.height_fraction <= 0:
            raise ValueError(
                "height_fraction must be greater than 0"
            )

        if (
            self.x_fraction
            + self.width_fraction
            > 1.0
        ):
            raise ValueError(
                "progress region exceeds card width"
            )

        if (
            self.y_fraction
            + self.height_fraction
            > 1.0
        ):
            raise ValueError(
                "progress region exceeds card height"
            )


class BlueprintProgressRegionLocator:
    """
    由製作卡片區域計算進度文字區域。
    """

    def __init__(
        self,
        config: BlueprintProgressRegionConfig
        | None = None,
    ) -> None:
        self.config = (
            config
            or BlueprintProgressRegionConfig()
        )

    def locate(
        self,
        card_region: ImageRegion,
    ) -> ImageRegion:
        if not isinstance(card_region, ImageRegion):
            raise TypeError(
                "card_region must be ImageRegion"
            )

        x = (
            card_region.x
            + round(
                card_region.width
                * self.config.x_fraction
            )
        )

        y = (
            card_region.y
            + round(
                card_region.height
                * self.config.y_fraction
            )
        )

        width = max(
            1,
            round(
                card_region.width
                * self.config.width_fraction
            ),
        )

        height = max(
            1,
            round(
                card_region.height
                * self.config.height_fraction
            ),
        )

        return ImageRegion(
            x=x,
            y=y,
            width=width,
            height=height,
        )