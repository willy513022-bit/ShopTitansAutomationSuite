from __future__ import annotations

from ai.action import Action, ActionType
from ai.game_state import GameState
from ai.policies import (
    EnergyPolicy,
    MarketPolicy,
    QuestPolicy,
)


class PriorityEngine:
    def __init__(
        self,
        energy_policy: EnergyPolicy | None = None,
        quest_policy: QuestPolicy | None = None,
        market_policy: MarketPolicy | None = None,
    ) -> None:
        self.energy_policy = (
            energy_policy
            or EnergyPolicy()
        )

        self.quest_policy = (
            quest_policy
            or QuestPolicy()
        )

        self.market_policy = (
            market_policy
            or MarketPolicy()
        )

    def build_actions(
        self,
        state: GameState,
    ) -> list[Action]:
        actions: list[Action] = []

        actions.extend(
            self._collection_actions(state)
        )

        actions.extend(
            self._quest_actions(state)
        )

        actions.extend(
            self._craft_actions(state)
        )

        actions.extend(
            self._customer_actions(state)
        )

        actions.extend(
            self._market_actions(state)
        )

        if not actions:
            actions.append(
                Action(
                    action_type=ActionType.WAIT,
                    score=0,
                    reason="目前沒有可執行任務",
                )
            )

        return sorted(
            actions,
            key=lambda action: action.score,
            reverse=True,
        )

    def _collection_actions(
        self,
        state: GameState,
    ) -> list[Action]:
        actions: list[Action] = []

        for task in state.collection_tasks:
            base = float(task.priority)

            if task.ready_to_donate:
                actions.append(
                    Action(
                        ActionType.DONATE_COLLECTION,
                        base + 20,
                        (
                            f"{task.item_name} "
                            f"{task.target_quality} "
                            "已可捐入收藏冊"
                        ),
                        {
                            "task_id": task.task_id,
                            "item_id": task.item_id,
                            "quality": (
                                task.target_quality
                            ),
                        },
                    )
                )

            elif task.ready_to_fuse:
                actions.append(
                    Action(
                        ActionType.START_FUSION,
                        base + 12,
                        (
                            f"{task.item_name} "
                            "已具備融合條件"
                        ),
                        {
                            "task_id": task.task_id,
                            "item_id": task.item_id,
                            "quality": (
                                task.target_quality
                            ),
                        },
                    )
                )

            elif (
                task.ready_to_craft
                and state.free_craft_slots > 0
            ):
                actions.append(
                    Action(
                        ActionType.START_CRAFT,
                        base + 8,
                        (
                            f"{task.item_name} "
                            "可立即製作"
                        ),
                        {
                            "task_id": task.task_id,
                            "item_id": task.item_id,
                        },
                    )
                )

        return actions

    def _quest_actions(
        self,
        state: GameState,
    ) -> list[Action]:
        actions: list[Action] = []

        for quest_id in state.completed_quest_ids:
            actions.append(
                Action(
                    ActionType.CLAIM_QUEST,
                    98,
                    "冒險已完成，應優先領取",
                    {"quest_id": quest_id},
                )
            )

        needed_materials = {
            material
            for task in state.collection_tasks
            for material in task.missing_materials
        }

        for quest in state.quest_options:
            if not quest.ready:
                continue

            if (
                quest.material_name
                not in needed_materials
            ):
                continue

            if (
                quest.party_face_status
                not in self.quest_policy
                .allowed_face_statuses
            ):
                continue

            actions.append(
                Action(
                    ActionType.START_QUEST,
                    93,
                    (
                        f"冒險可取得缺少素材："
                        f"{quest.material_name}"
                    ),
                    {
                        "quest_id": quest.quest_id,
                        "area_name": quest.area_name,
                        "material_name": (
                            quest.material_name
                        ),
                    },
                )
            )

        return actions

    def _craft_actions(
        self,
        state: GameState,
    ) -> list[Action]:
        actions: list[Action] = []

        for job_id in (
            state.completed_craft_job_ids
        ):
            actions.append(
                Action(
                    ActionType.CLAIM_CRAFT,
                    97,
                    "製作已完成，應優先領取",
                    {"job_id": job_id},
                )
            )

        energy_ratio = state.energy.ratio

        if (
            energy_ratio
            >= self.energy_policy
            .overflow_risk_ratio
            and self.energy_policy
            .allow_energy_speedup
        ):
            candidates = [
                job
                for job in state.craft_jobs
                if job.can_speed_up_with_energy
            ]

            if candidates:
                target = max(
                    candidates,
                    key=lambda job: (
                        job.collection_related,
                        job.priority,
                        job.remaining_seconds,
                    ),
                )

                actions.append(
                    Action(
                        ActionType.SPEED_UP_CRAFT,
                        94,
                        (
                            "能量接近上限，"
                            f"加速 {target.item_name}"
                        ),
                        {
                            "job_id": target.job_id,
                            "item_id": target.item_id,
                            "use_energy_only": True,
                            "allow_gems": False,
                        },
                    )
                )

        return actions

    def _customer_actions(
        self,
        state: GameState,
    ) -> list[Action]:
        actions: list[Action] = []
        ratio = state.energy.ratio

        for customer in state.customers:
            if customer.reserved:
                continue

            if (
                ratio
                < self.energy_policy
                .low_energy_ratio
                and customer.can_small_talk
                and self.energy_policy
                .allow_small_talk_at_low_energy
            ):
                actions.append(
                    Action(
                        ActionType.SMALL_TALK,
                        88,
                        (
                            "目前能量偏低，"
                            "閒談失敗的實際損失有限"
                        ),
                        {
                            "customer_id": (
                                customer.customer_id
                            ),
                        },
                    )
                )

            if (
                ratio
                < self.energy_policy
                .high_energy_ratio
                and customer.can_discount
                and customer.item_value
                <= self.energy_policy
                .cheap_item_value
            ):
                actions.append(
                    Action(
                        ActionType.DISCOUNT,
                        75,
                        (
                            f"{customer.item_name} "
                            "價值低，適合折扣換能量"
                        ),
                        {
                            "customer_id": (
                                customer.customer_id
                            ),
                            "item_id": customer.item_id,
                        },
                    )
                )

            if (
                ratio
                >= self.energy_policy
                .high_energy_ratio
                and customer.can_surcharge
                and customer.item_value
                >= self.energy_policy
                .high_item_value
            ):
                score = (
                    96
                    if ratio
                    >= self.energy_policy
                    .overflow_risk_ratio
                    else 90
                )

                actions.append(
                    Action(
                        ActionType.SURCHARGE,
                        score,
                        (
                            f"{customer.item_name} "
                            "價值高，適合加價"
                        ),
                        {
                            "customer_id": (
                                customer.customer_id
                            ),
                            "item_id": customer.item_id,
                        },
                    )
                )

            actions.append(
                Action(
                    ActionType.NORMAL_SELL,
                    50,
                    (
                        f"{customer.item_name} "
                        "可正常出售"
                    ),
                    {
                        "customer_id": (
                            customer.customer_id
                        ),
                        "item_id": customer.item_id,
                    },
                )
            )

        return actions

    def _market_actions(
        self,
        state: GameState,
    ) -> list[Action]:
        if not self.market_policy.enabled:
            return []

        actions: list[Action] = []

        for offer in state.market_opportunities:
            total_cost = (
                offer.quantity_needed
                * offer.unit_price
            )

            if not offer.affordable_by_policy:
                continue

            if (
                total_cost
                > self.market_policy
                .single_purchase_limit
            ):
                continue

            remaining_gold = (
                state.currencies.gold
                - total_cost
            )

            if (
                remaining_gold
                < self.market_policy
                .minimum_gold_reserve
            ):
                continue

            actions.append(
                Action(
                    ActionType.BUY_MARKET,
                    82,
                    (
                        f"市場可低價購買 "
                        f"{offer.item_name}"
                    ),
                    {
                        "item_name": offer.item_name,
                        "quantity": (
                            offer.quantity_needed
                        ),
                        "unit_price": offer.unit_price,
                        "total_cost": total_cost,
                        "gold_only": True,
                    },
                )
            )

        return actions
