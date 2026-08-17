from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class WorkerRequirement:
    worker: str
    level: int

    def __post_init__(self) -> None:
        worker = self.worker.strip()

        if not worker:
            raise ValueError(
                "worker is required"
            )

        if self.level < 0:
            raise ValueError(
                "level cannot be negative"
            )

        object.__setattr__(
            self,
            "worker",
            worker,
        )


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    item_id: str | None
    name: str
    quantity: int
    resource_type: str = "item"

    quality: str | None = None
    source_column: str | None = None

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise ValueError(
                "ingredient name is required"
            )

        if self.quantity < 0:
            raise ValueError(
                "ingredient quantity cannot be negative"
            )

        resource_type = (
            self.resource_type.strip()
            or "item"
        )

        quality = (
            self.quality.strip()
            if isinstance(
                self.quality,
                str,
            )
            and self.quality.strip()
            else None
        )

        source_column = (
            self.source_column.strip()
            if isinstance(
                self.source_column,
                str,
            )
            and self.source_column.strip()
            else None
        )

        object.__setattr__(
            self,
            "name",
            name,
        )

        object.__setattr__(
            self,
            "resource_type",
            resource_type,
        )

        object.__setattr__(
            self,
            "quality",
            quality,
        )

        object.__setattr__(
            self,
            "source_column",
            source_column,
        )


@dataclass(frozen=True, slots=True)
class GameItem:
    item_id: str
    name: str
    item_type: str
    tier: int
    craft_time_seconds: int

    base_value: int = 0

    required_workers: tuple[
        WorkerRequirement,
        ...
    ] = field(
        default_factory=tuple
    )

    ingredients: tuple[
        RecipeIngredient,
        ...
    ] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        item_id = self.item_id.strip()
        name = self.name.strip()
        item_type = (
            self.item_type.strip()
            or "Unknown"
        )

        if not item_id:
            raise ValueError(
                "item_id is required"
            )

        if not name:
            raise ValueError(
                "name is required"
            )

        if self.tier < 0:
            raise ValueError(
                "tier cannot be negative"
            )

        if self.craft_time_seconds < 0:
            raise ValueError(
                "craft_time_seconds cannot be negative"
            )

        if self.base_value < 0:
            raise ValueError(
                "base_value cannot be negative"
            )

        object.__setattr__(
            self,
            "item_id",
            item_id,
        )

        object.__setattr__(
            self,
            "name",
            name,
        )

        object.__setattr__(
            self,
            "item_type",
            item_type,
        )

        object.__setattr__(
            self,
            "required_workers",
            tuple(
                self.required_workers
            ),
        )

        object.__setattr__(
            self,
            "ingredients",
            tuple(
                self.ingredients
            ),
        )

    @property
    def components(
        self,
    ) -> tuple[
        RecipeIngredient,
        ...
    ]:
        return tuple(
            ingredient
            for ingredient
            in self.ingredients
            if ingredient.resource_type
            in {
                "item",
                "quest_component",
            }
        )

    @property
    def raw_resources(
        self,
    ) -> tuple[
        RecipeIngredient,
        ...
    ]:
        return tuple(
            ingredient
            for ingredient
            in self.ingredients
            if ingredient.resource_type
            == "resource"
        )