import pytest

from vision.blueprint_card_locator import (
    BlueprintCard,
    BlueprintCardGridConfig,
    BlueprintCardLocator,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)


def test_default_config():
    config = BlueprintCardGridConfig()

    assert config.column_count == 3
    assert config.card_width == 207
    assert config.card_height == 250
    assert config.column_step == 211
    assert config.row_step == 262


def test_locate_single_visible_row():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=1000,
        image_width=878,
        image_height=1250,
    )

    assert len(cards) == 3

    assert cards[0].row == 0
    assert cards[0].column == 0

    assert cards[1].row == 0
    assert cards[1].column == 1

    assert cards[2].row == 0
    assert cards[2].column == 2


def test_locate_two_rows():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=700,
        image_width=878,
        image_height=1300,
    )

    assert len(cards) == 6

    assert [
        (card.row, card.column)
        for card in cards
    ] == [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
    ]


def test_column_coordinates():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=500,
        image_width=878,
        image_height=800,
    )

    assert [
        card.x
        for card in cards
    ] == [
        22,
        233,
        444,
    ]


def test_row_coordinates():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=500,
        image_width=878,
        image_height=1100,
    )

    assert len(cards) == 6

    assert cards[0].y == 500
    assert cards[3].y == 762


def test_card_region_is_image_region():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=500,
        image_width=878,
        image_height=800,
    )

    assert isinstance(
        cards[0],
        BlueprintCard,
    )

    assert isinstance(
        cards[0].region,
        ImageRegion,
    )

    assert cards[0].region == ImageRegion(
        x=22,
        y=500,
        width=207,
        height=250,
    )


def test_partial_bottom_row_is_not_returned():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=1000,
        image_width=878,
        image_height=1400,
    )

    # Row 0:
    # 1000 -> 1250
    #
    # Row 1:
    # 1262 -> 1512
    #
    # 第二列超出畫面，所以只有第一列。
    assert len(cards) == 3


def test_partial_right_column_is_not_returned():
    locator = BlueprintCardLocator()

    cards = locator.locate(
        first_card_x=22,
        first_card_y=500,
        image_width=600,
        image_height=800,
    )

    # col 0:
    # x=22 -> 229
    #
    # col 1:
    # x=233 -> 440
    #
    # col 2:
    # x=444 -> 651
    #
    # 第三欄超出。
    assert len(cards) == 2

    assert [
        card.column
        for card in cards
    ] == [
        0,
        1,
    ]


def test_custom_config():
    config = BlueprintCardGridConfig(
        column_count=2,
        card_width=100,
        card_height=150,
        column_step=120,
        row_step=170,
    )

    locator = BlueprintCardLocator(
        config=config
    )

    cards = locator.locate(
        first_card_x=10,
        first_card_y=20,
        image_width=500,
        image_height=400,
    )

    assert len(cards) == 4

    assert cards[0].region == ImageRegion(
        x=10,
        y=20,
        width=100,
        height=150,
    )

    assert cards[1].region == ImageRegion(
        x=130,
        y=20,
        width=100,
        height=150,
    )

    assert cards[2].region == ImageRegion(
        x=10,
        y=190,
        width=100,
        height=150,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "column_count": 0,
        },
        {
            "card_width": 0,
        },
        {
            "card_height": 0,
        },
        {
            "column_step": 0,
        },
        {
            "row_step": 0,
        },
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        BlueprintCardGridConfig(
            **kwargs
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "image_width": 0,
        },
        {
            "image_height": 0,
        },
        {
            "maximum_rows": 0,
        },
        {
            "first_card_x": -1,
        },
        {
            "first_card_y": -1,
        },
    ],
)
def test_invalid_locate_arguments(kwargs):
    locator = BlueprintCardLocator()

    arguments = {
        "first_card_x": 22,
        "first_card_y": 500,
        "image_width": 878,
        "image_height": 1000,
        "maximum_rows": 20,
    }

    arguments.update(
        kwargs
    )

    with pytest.raises(ValueError):
        locator.locate(
            **arguments
        )