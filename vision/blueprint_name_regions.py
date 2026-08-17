from __future__ import annotations

from dataclasses import dataclass

from vision.blueprint_progress_models import ImageRegion


@dataclass(frozen=True, slots=True)
class BlueprintNameRegionConfig:
    x_fraction: float = 0.06
    y_fraction: float = 0.40
    width_fraction: float = 0.88
    height_fraction: float = 0.16

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
                "name region exceeds card width"
            )

        if (
            self.y_fraction
            + self.height_fraction
            > 1.0
        ):
            raise ValueError(
                "name region exceeds card height"
            )


class BlueprintNameRegionLocator:
    def __init__(
        self,
        config: BlueprintNameRegionConfig
        | None = None,
    ) -> None:
        self.config = (
            config
            or BlueprintNameRegionConfig()
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