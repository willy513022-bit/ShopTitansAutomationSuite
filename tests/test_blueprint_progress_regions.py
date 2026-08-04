import pytest

from vision.blueprint_progress_models import (
    ImageRegion,
)
from vision.blueprint_progress_regions import (
    BlueprintProgressRegionConfig,
    BlueprintProgressRegionLocator,
)


def test_default_region_is_inside_card():
    card = ImageRegion(
        x=100,
        y=200,
        width=400,
        height=500,
    )

    region = (
        BlueprintProgressRegionLocator()
        .locate(card)
    )

    assert region.left >= card.left
    assert region.top >= card.top
    assert region.right <= card.right
    assert region.bottom <= card.bottom


def test_default_region_coordinates():
    card = ImageRegion(
        x=100,
        y=200,
        width=400,
        height=500,
    )

    region = (
        BlueprintProgressRegionLocator()
        .locate(card)
    )

    assert region.x == 160
    assert region.y == 580
    assert region.width == 280
    assert region.height == 90


def test_custom_region_config():
    config = BlueprintProgressRegionConfig(
        x_fraction=0.25,
        y_fraction=0.50,
        width_fraction=0.50,
        height_fraction=0.25,
    )

    locator = BlueprintProgressRegionLocator(
        config
    )

    card = ImageRegion(
        x=0,
        y=0,
        width=200,
        height=400,
    )

    region = locator.locate(card)

    assert region == ImageRegion(
        x=50,
        y=200,
        width=100,
        height=100,
    )


def test_invalid_fraction_rejected():
    with pytest.raises(ValueError):
        BlueprintProgressRegionConfig(
            x_fraction=-0.1,
        )


def test_region_cannot_exceed_width():
    with pytest.raises(ValueError):
        BlueprintProgressRegionConfig(
            x_fraction=0.50,
            width_fraction=0.75,
        )


def test_locator_rejects_unknown_object():
    with pytest.raises(TypeError):
        BlueprintProgressRegionLocator().locate(
            object()
        )