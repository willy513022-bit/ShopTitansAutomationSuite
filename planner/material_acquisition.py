from __future__ import annotations

from dataclasses import dataclass

from planner.models import (
    AcquisitionMethod,
    MaterialNeed,
    PlannedStep,
)
from planner.quest_risk import QuestRiskPolicy


@dataclass(frozen=True)
class AcquisitionPolicy:
    minimum_gold_reserve: int = 5_000_000
    single_purchase_limit: int = 250_000
    allow_market: bool = True
    allow_quest: bool = True
    prefer_market_when_cheaper: bool = True


class MaterialAcquisitionPlanner:
    def __init__(
        self,
        quest_policy: QuestRiskPolicy | None = None,
        policy: AcquisitionPolicy | None = None,
    ) -> None:
        self.quest_policy = (
            quest_policy
            or QuestRiskPolicy()
        )

        self.policy = (
            policy
            or AcquisitionPolicy()
        )

    def plan(
        self,
        task_id: str,
        need: MaterialNeed,
        current_gold: int,
        base_score: float,
    ) -> tuple[PlannedStep | None, str | None]:
        missing = max(
            0,
            need.quantity
            - need.inventory_quantity,
        )

        if missing <= 0:
            return (
                PlannedStep(
                    method=AcquisitionMethod.INVENTORY,
                    task_id=task_id,
                    score=base_score + 15,
                    reason=(
                        f"{need.item_name} "
                        "庫存已足夠"
                    ),
                    payload={
                        "item_name": need.item_name,
                        "quantity": need.quantity,
                    },
                ),
                None,
            )

        market_step = self._market_step(
            task_id=task_id,
            need=need,
            missing=missing,
            current_gold=current_gold,
            base_score=base_score,
        )

        quest_step, quest_block_reason = (
            self._quest_step(
                task_id=task_id,
                need=need,
                missing=missing,
                base_score=base_score,
            )
        )

        if market_step and quest_step:
            if self.policy.prefer_market_when_cheaper:
                return market_step, None
            return quest_step, None

        if market_step:
            return market_step, None

        if quest_step:
            return quest_step, None

        if quest_block_reason:
            return None, quest_block_reason

        if need.market_quote is not None:
            return (
                None,
                (
                    f"{need.item_name} "
                    "市場價格超過允許上限"
                ),
            )

        return (
            None,
            (
                f"{need.item_name} "
                "目前沒有可用取得方式"
            ),
        )

    def _market_step(
        self,
        task_id: str,
        need: MaterialNeed,
        missing: int,
        current_gold: int,
        base_score: float,
    ) -> PlannedStep | None:
        if not self.policy.allow_market:
            return None

        quote = need.market_quote

        if quote is None:
            return None

        if not quote.gold_only:
            return None

        if quote.quantity_available < missing:
            return None

        if (
            need.max_unit_price is not None
            and quote.unit_price
            > need.max_unit_price
        ):
            return None

        total_cost = (
            quote.unit_price
            * missing
        )

        if (
            total_cost
            > self.policy.single_purchase_limit
        ):
            return None

        if (
            current_gold - total_cost
            < self.policy.minimum_gold_reserve
        ):
            return None

        return PlannedStep(
            method=AcquisitionMethod.MARKET,
            task_id=task_id,
            score=base_score + 8,
            reason=(
                f"{need.item_name} "
                "可用金幣低價購買"
            ),
            payload={
                "item_name": need.item_name,
                "quantity": missing,
                "unit_price": quote.unit_price,
                "total_cost": total_cost,
                "gold_only": True,
            },
        )

    def _quest_step(
        self,
        task_id: str,
        need: MaterialNeed,
        missing: int,
        base_score: float,
    ) -> tuple[PlannedStep | None, str | None]:
        if not self.policy.allow_quest:
            return None, None

        if need.quest_area is None:
            return None, None

        best_party = (
            self.quest_policy
            .choose_best_party(
                need.quest_parties
            )
        )

        if best_party is None:
            attempted = len(
                need.quest_parties
            )

            best_status = (
                need.quest_parties[0].face_status
                if need.quest_parties
                else "NONE"
            )

            return (
                None,
                (
                    f"{need.item_name} 需要冒險取得，"
                    f"但 {attempted} 組隊伍皆未達安全門檻；"
                    f"最佳狀態：{best_status}"
                ),
            )

        return (
            PlannedStep(
                method=AcquisitionMethod.QUEST,
                task_id=task_id,
                score=base_score + 10,
                reason=(
                    f"派遣 {best_party.party_id} "
                    f"前往 {need.quest_area} "
                    f"取得 {need.item_name}"
                ),
                payload={
                    "item_name": need.item_name,
                    "quantity_needed": missing,
                    "quest_area": need.quest_area,
                    "party_id": best_party.party_id,
                    "face_status": (
                        best_party.face_status
                    ),
                },
            ),
            None,
        )
