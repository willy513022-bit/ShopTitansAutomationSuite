from __future__ import annotations

from planner.material_acquisition import (
    MaterialAcquisitionPlanner,
)
from planner.models import (
    AcquisitionMethod,
    CollectionPlan,
    CollectionTarget,
    CollectionTaskStatus,
    PlannedStep,
)


class CollectionPlanner:
    def __init__(
        self,
        acquisition_planner: (
            MaterialAcquisitionPlanner | None
        ) = None,
    ) -> None:
        self.acquisition_planner = (
            acquisition_planner
            or MaterialAcquisitionPlanner()
        )

    def build_plan(
        self,
        targets: list[CollectionTarget],
        current_gold: int,
        free_craft_slots: int,
    ) -> CollectionPlan:
        statuses: dict[
            str,
            CollectionTaskStatus,
        ] = {}

        blocked_reasons: dict[
            str,
            str,
        ] = {}

        steps: list[PlannedStep] = []

        ordered_targets = sorted(
            targets,
            key=lambda target: (
                target.priority
            ),
            reverse=True,
        )

        for target in ordered_targets:
            if target.completed:
                statuses[target.task_id] = (
                    CollectionTaskStatus.COMPLETED
                )
                continue

            if target.ready_to_donate:
                statuses[target.task_id] = (
                    CollectionTaskStatus
                    .READY_TO_DONATE
                )

                steps.append(
                    PlannedStep(
                        method=(
                            AcquisitionMethod.DONATE
                        ),
                        task_id=target.task_id,
                        score=target.priority + 20,
                        reason=(
                            f"{target.item_name} "
                            f"{target.target_quality} "
                            "已可捐入收藏冊"
                        ),
                        payload={
                            "item_id": target.item_id,
                            "quality": (
                                target.target_quality
                            ),
                        },
                    )
                )
                continue

            if target.ready_to_fuse:
                statuses[target.task_id] = (
                    CollectionTaskStatus
                    .WAITING_FUSION
                )

                steps.append(
                    PlannedStep(
                        method=(
                            AcquisitionMethod.FUSION
                        ),
                        task_id=target.task_id,
                        score=target.priority + 12,
                        reason=(
                            f"{target.item_name} "
                            "已具備融合條件"
                        ),
                        payload={
                            "item_id": target.item_id,
                            "quality": (
                                target.target_quality
                            ),
                        },
                    )
                )
                continue

            if (
                target.ready_to_craft
                and free_craft_slots > 0
            ):
                statuses[target.task_id] = (
                    CollectionTaskStatus
                    .WAITING_CRAFT
                )

                steps.append(
                    PlannedStep(
                        method=(
                            AcquisitionMethod.CRAFT
                        ),
                        task_id=target.task_id,
                        score=target.priority + 8,
                        reason=(
                            f"{target.item_name} "
                            "材料足夠，可開始製作"
                        ),
                        payload={
                            "item_id": target.item_id,
                        },
                    )
                )
                continue

            if target.material_needs:
                task_blocked = False

                for need in target.material_needs:
                    step, blocked = (
                        self.acquisition_planner.plan(
                            task_id=target.task_id,
                            need=need,
                            current_gold=current_gold,
                            base_score=(
                                float(target.priority)
                            ),
                        )
                    )

                    if step is not None:
                        if (
                            step.method
                            == AcquisitionMethod.QUEST
                        ):
                            statuses[
                                target.task_id
                            ] = (
                                CollectionTaskStatus
                                .WAITING_QUEST
                            )

                        elif (
                            step.method
                            == AcquisitionMethod.MARKET
                        ):
                            statuses[
                                target.task_id
                            ] = (
                                CollectionTaskStatus
                                .WAITING_MARKET
                            )

                        else:
                            statuses[
                                target.task_id
                            ] = (
                                CollectionTaskStatus.READY
                            )

                        steps.append(step)
                        task_blocked = False
                        break

                    if blocked is not None:
                        task_blocked = True
                        blocked_reasons[
                            target.task_id
                        ] = blocked

                if task_blocked:
                    reason = blocked_reasons[
                        target.task_id
                    ]

                    if "隊伍皆未達安全門檻" in reason:
                        statuses[
                            target.task_id
                        ] = (
                            CollectionTaskStatus
                            .BLOCKED_NO_SAFE_PARTY
                        )
                    elif "市場價格" in reason:
                        statuses[
                            target.task_id
                        ] = (
                            CollectionTaskStatus
                            .BLOCKED_MARKET_PRICE
                        )
                    else:
                        statuses[
                            target.task_id
                        ] = (
                            CollectionTaskStatus
                            .BLOCKED_RESOURCE
                        )

                continue

            statuses[target.task_id] = (
                CollectionTaskStatus
                .BLOCKED_RESOURCE
            )

            blocked_reasons[
                target.task_id
            ] = "目前沒有可執行步驟"

        ranked_steps = tuple(
            sorted(
                steps,
                key=lambda step: step.score,
                reverse=True,
            )
        )

        selected_step = (
            ranked_steps[0]
            if ranked_steps
            else None
        )

        return CollectionPlan(
            selected_task_id=(
                selected_step.task_id
                if selected_step
                else None
            ),
            selected_step=selected_step,
            task_statuses=statuses,
            blocked_reasons=blocked_reasons,
            ranked_steps=ranked_steps,
        )
