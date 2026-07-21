from __future__ import annotations

from dataclasses import dataclass

from events.models import EventCraftOption


@dataclass(frozen=True)
class KingsCapriceDecision:
    selected_item_id: str | None
    reason: str
    ranked_item_ids: tuple[str, ...]


class KingsCapricePlanner:
    def choose(
        self,
        options: list[EventCraftOption],
    ) -> KingsCapriceDecision:
        feasible = [
            option
            for option in options
            if option.resources_available
            and not option.collection_conflict
            and not option.hero_conflict
        ]

        if not feasible:
            return KingsCapriceDecision(
                selected_item_id=None,
                reason="所有活動指定物品目前皆被阻塞",
                ranked_item_ids=(),
            )

        ranked = sorted(
            feasible,
            key=lambda option: (
                option.points
                / max(option.craft_time_seconds, 1),
                option.points,
            ),
            reverse=True,
        )

        selected = ranked[0]

        return KingsCapriceDecision(
            selected_item_id=selected.item_id,
            reason=(
                f"選擇 {selected.item_name}："
                "資源足夠且分數效率最高"
            ),
            ranked_item_ids=tuple(
                option.item_id
                for option in ranked
            ),
        )
