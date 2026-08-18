from __future__ import annotations

import json

import pytest

from knowledge.clickmap_registry import (
    ClickMapRegistry,
)
from runtime.clickmap_target_resolver import (
    ClickMapTargetResolver,
)


def make_registry(
    tmp_path,
):
    path = (
        tmp_path
        / "shop_878x1550.json"
    )

    path.write_text(
        json.dumps(
            {
                "resolution": "878x1550",
                "points": {
                    "production_button": [
                        700,
                        1400,
                    ],
                    "craft_tab": [
                        300,
                        200,
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    return (
        ClickMapRegistry()
        .load_file(path)
    )


def test_resolves_production_button(
    tmp_path,
):
    resolver = ClickMapTargetResolver(
        make_registry(tmp_path),
        "878x1550",
    )

    target = resolver.resolve(
        "production_button"
    )

    assert target.x == 700
    assert target.y == 1400

    assert (
        target.name
        == "production_button"
    )

    assert (
        target.source
        == "clickmap:878x1550"
    )


def test_resolves_craft_tab(
    tmp_path,
):
    resolver = ClickMapTargetResolver(
        make_registry(tmp_path),
        "878x1550",
    )

    target = resolver.resolve(
        "craft_tab"
    )

    assert target.position == (
        300,
        200,
    )


def test_unknown_target_raises(
    tmp_path,
):
    resolver = ClickMapTargetResolver(
        make_registry(tmp_path),
        "878x1550",
    )

    with pytest.raises(KeyError):
        resolver.resolve(
            "unknown_button"
        )


def test_wrong_resolution_raises(
    tmp_path,
):
    resolver = ClickMapTargetResolver(
        make_registry(tmp_path),
        "1920x1080",
    )

    with pytest.raises(KeyError):
        resolver.resolve(
            "production_button"
        )


def test_empty_target_rejected(
    tmp_path,
):
    resolver = ClickMapTargetResolver(
        make_registry(tmp_path),
        "878x1550",
    )

    with pytest.raises(ValueError):
        resolver.resolve("")


def test_empty_resolution_rejected(
    tmp_path,
):
    with pytest.raises(ValueError):
        ClickMapTargetResolver(
            make_registry(tmp_path),
            "",
        )


def test_invalid_registry_rejected():
    with pytest.raises(TypeError):
        ClickMapTargetResolver(
            object(),
            "878x1550",
        )