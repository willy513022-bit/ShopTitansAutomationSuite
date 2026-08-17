from __future__ import annotations

from dataclasses import dataclass

from vision.blueprint_progress_models import ImageRegion


@dataclass(frozen=True, slots=True)
class BlueprintCardGridConfig:
    """
    Craft 畫面的 Blueprint 卡片網格設定。

    Shop Titans Craft 清單目前為固定三欄排列。

    Locator v1 不負責：
    - OCR
    - 判斷物品名稱
    - 判斷 Tier
    - 判斷卡片是否可製作

    它只負責根據已知的第一張卡片位置，
    建立畫面上所有可能的卡片 ImageRegion。
    """

    column_count: int = 3

    card_width: int = 207
    card_height: int = 250

    column_step: int = 211
    row_step: int = 262

    def __post_init__(self) -> None:
        if self.column_count <= 0:
            raise ValueError(
                "column_count must be positive"
            )

        if self.card_width <= 0:
            raise ValueError(
                "card_width must be positive"
            )

        if self.card_height <= 0:
            raise ValueError(
                "card_height must be positive"
            )

        if self.column_step <= 0:
            raise ValueError(
                "column_step must be positive"
            )

        if self.row_step <= 0:
            raise ValueError(
                "row_step must be positive"
            )


@dataclass(frozen=True, slots=True)
class BlueprintCard:
    row: int
    column: int
    region: ImageRegion

    @property
    def x(self) -> int:
        return self.region.x

    @property
    def y(self) -> int:
        return self.region.y

    @property
    def width(self) -> int:
        return self.region.width

    @property
    def height(self) -> int:
        return self.region.height


class BlueprintCardLocator:
    """
    Blueprint Craft 卡片網格定位器。

    v1 使用一個已知 anchor：

        first_card_x
        first_card_y

    然後依三欄 Grid 推算其他卡片。

    注意：
    這不是最終的視覺偵測版本。

    最終版本可以改成：

        Craft panel detection
            ↓
        first card / tier badge detection
            ↓
        grid generation

    目前先把「Grid 幾何定位」獨立驗證成功。
    """

    def __init__(
        self,
        config: BlueprintCardGridConfig | None = None,
    ) -> None:
        self.config = (
            config
            if config is not None
            else BlueprintCardGridConfig()
        )

    def locate(
        self,
        *,
        first_card_x: int,
        first_card_y: int,
        image_width: int,
        image_height: int,
        maximum_rows: int = 20,
    ) -> list[BlueprintCard]:
        if image_width <= 0:
            raise ValueError(
                "image_width must be positive"
            )

        if image_height <= 0:
            raise ValueError(
                "image_height must be positive"
            )

        if maximum_rows <= 0:
            raise ValueError(
                "maximum_rows must be positive"
            )

        if first_card_x < 0:
            raise ValueError(
                "first_card_x cannot be negative"
            )

        if first_card_y < 0:
            raise ValueError(
                "first_card_y cannot be negative"
            )

        cards: list[BlueprintCard] = []

        for row in range(maximum_rows):
            y = (
                first_card_y
                + row * self.config.row_step
            )

            # 如果這一整列已經超出畫面，
            # 後面的 row 也一定超出。
            if y >= image_height:
                break

            # 不加入只有一小部分露在底部的卡片。
            if (
                y + self.config.card_height
                > image_height
            ):
                break

            for column in range(
                self.config.column_count
            ):
                x = (
                    first_card_x
                    + column
                    * self.config.column_step
                )

                if x >= image_width:
                    continue

                if (
                    x + self.config.card_width
                    > image_width
                ):
                    continue

                region = ImageRegion(
                    x=x,
                    y=y,
                    width=self.config.card_width,
                    height=self.config.card_height,
                )

                cards.append(
                    BlueprintCard(
                        row=row,
                        column=column,
                        region=region,
                    )
                )

        return cards