import pytest

from vision.blueprint_name_regions import (
    BlueprintNameRegionConfig,
    BlueprintNameRegionLocator,
)
from vision.blueprint_progress_models import (
    ImageRegion,
)


def test_default_name_region():
    locator = (
        BlueprintNameRegionLocator()
    )

    card = ImageRegion(
        x=438,
        y=1011,
        width=207,
        height=250,
    )

    region = locator.locate(
        card
    )

    assert region.x == 450
    assert region.y == 1111
    assert region.width == 182
    assert region.height == 40


def test_region_is_inside_card():
    locator = (
        BlueprintNameRegionLocator()
    )

    card = ImageRegion(
        x=100,
        y=200,
        width=207,
        height=250,
    )

    region = locator.locate(
        card
    )

    assert region.left >= card.left
    assert region.top >= card.top
    assert region.right <= card.right
    assert region.bottom <= card.bottom


def test_custom_config():
    locator = BlueprintNameRegionLocator(
        BlueprintNameRegionConfig(
            x_fraction=0.10,
            y_fraction=0.20,
            width_fraction=0.50,
            height_fraction=0.10,
        )
    )

    card = ImageRegion(
        x=100,
        y=200,
        width=200,
        height=300,
    )

    region = locator.locate(
        card
    )

    assert region == ImageRegion(
        x=120,
        y=260,
        width=100,
        height=30,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "x_fraction": -0.1,
        },
        {
            "y_fraction": 1.1,
        },
        {
            "width_fraction": 0.0,
        },
        {
            "height_fraction": 0.0,
        },
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        BlueprintNameRegionConfig(
            **kwargs
        )


def test_region_cannot_exceed_width():
    with pytest.raises(ValueError):
        BlueprintNameRegionConfig(
            x_fraction=0.5,
            width_fraction=0.6,
        )


def test_region_cannot_exceed_height():
    with pytest.raises(ValueError):
        BlueprintNameRegionConfig(
            y_fraction=0.9,
            height_fraction=0.2,
        )


def test_locator_rejects_unknown_object():
    locator = (
        BlueprintNameRegionLocator()
    )

    with pytest.raises(TypeError):
        locator.locate(
            object()
        )