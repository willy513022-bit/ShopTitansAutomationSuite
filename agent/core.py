from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable
import json


@dataclass(slots=True)
class ScreenState:
    name: str = "UNKNOWN"
    confidence: float = 0.0


@dataclass(slots=True)
class WorldState:
    screen: ScreenState = field(default_factory=ScreenState)
    queue_remaining: int | None = None
    ready_count: int = 0
    customer_count: int = 0
    energy: int = 0
    gold: int = 0
    guild_objective: str | None = None
    previous_screen: str | None = None
    current_task: str | None = None
    unknown_reason: str | None = None
    applied_rules: list[str] = field(default_factory=list)

    @property
    def is_unknown(self) -> bool:
        return self.unknown_reason is not None


ScoreFn = Callable[[WorldState], dict[str, float]]
ConditionFn = Callable[[WorldState], bool]


@dataclass(slots=True)
class Task:
    name: str
    kind: str
    score_fn: ScoreFn
    condition: ConditionFn = lambda _state: True
    uses_diamond: bool = False
    gold_cost: int = 0
    energy_cost: int = 0


@dataclass(slots=True)
class Evaluation:
    task: str
    kind: str
    components: dict[str, float]
    total: float
    allowed: bool
    denied_reason: str | None = None


@dataclass(slots=True)
class Decision:
    selected_task: str | None
    score: float | None
    reason: str
    evaluations: list[Evaluation]


@dataclass(slots=True)
class SafetyPolicy:
    use_diamond: bool = False
    minimum_gold: int = 2_000_000_000
    minimum_energy: int = 1_500

    def validate(self, task: Task, state: WorldState) -> tuple[bool, str | None]:
        if task.uses_diamond and not self.use_diamond:
            return False, "禁止使用 Diamond"
        if state.gold - task.gold_cost < self.minimum_gold:
            return False, "Gold 將低於安全保留值"
        if state.energy - task.energy_cost < self.minimum_energy:
            return False, "Energy 將低於安全保留值"
        return True, None


class RuleEngine:
    def evaluate(self, state: WorldState) -> None:
        state.applied_rules.clear()

        if state.screen.confidence < 0.60:
            state.unknown_reason = (
                f"畫面辨識信心度過低：{state.screen.confidence:.0%}"
            )
            state.applied_rules.append("ST-001@v1")

        if state.screen.name.upper() == "UNKNOWN":
            state.unknown_reason = "無法辨識目前畫面"
            state.applied_rules.append("ST-002@v1")


class DecisionEngine:
    def __init__(self, safety: SafetyPolicy) -> None:
        self.safety = safety

    def choose(self, state: WorldState, tasks: list[Task]) -> Decision:
        evaluations: list[Evaluation] = []

        for task in tasks:
            if not task.condition(state):
                continue

            allowed, denied = self.safety.validate(task, state)
            components = task.score_fn(state)
            evaluations.append(
                Evaluation(
                    task=task.name,
                    kind=task.kind,
                    components=components,
                    total=sum(components.values()),
                    allowed=allowed,
                    denied_reason=denied,
                )
            )

        evaluations.sort(key=lambda x: x.total, reverse=True)
        allowed = [item for item in evaluations if item.allowed]

        if not allowed:
            return Decision(
                None, None, "沒有通過安全檢查的任務", evaluations
            )

        selected = allowed[0]
        return Decision(
            selected.task,
            selected.total,
            "選擇通過安全檢查且總分最高的任務",
            evaluations,
        )


class BlackBox:
    def __init__(self, output: Path, limit: int = 100) -> None:
        self.output = output
        self.output.mkdir(parents=True, exist_ok=True)
        self.frames = deque(maxlen=limit)

    def record(self, state: WorldState, decision: Decision | None, event: str) -> None:
        self.frames.append({
            "time": datetime.now().isoformat(),
            "event": event,
            "world_state": asdict(state),
            "decision": asdict(decision) if decision else None,
        })
        (self.output / "latest_100_frames.json").write_text(
            json.dumps(list(self.frames), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class UnknownNotebook:
    def __init__(self, output: Path) -> None:
        self.output = output
        self.output.mkdir(parents=True, exist_ok=True)

    def record(self, state: WorldState) -> Path:
        event_dir = self.output / (
            "unknown_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        )
        event_dir.mkdir()
        (event_dir / "world_state.json").write_text(
            json.dumps(asdict(state), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report = event_dir / "report.md"
        report.write_text(
            "# Unknown Event\n\n"
            f"- 原因：{state.unknown_reason}\n"
            f"- 畫面：{state.screen.name}\n"
            f"- 信心度：{state.screen.confidence:.1%}\n"
            f"- 上一畫面：{state.previous_screen}\n"
            f"- 當前任務：{state.current_task}\n"
            f"- 規則：{', '.join(state.applied_rules)}\n\n"
            "## Action\n\nSTOP — 未進行猜測性操作。\n",
            encoding="utf-8",
        )
        return report


def explain(decision: Decision) -> str:
    lines = ["Decision", "=" * 42]
    if decision.selected_task:
        lines += [
            f"選擇：{decision.selected_task}",
            f"分數：{decision.score:.1f}",
            f"原因：{decision.reason}",
        ]
    else:
        lines += ["未選擇任務", f"原因：{decision.reason}"]

    lines += ["", "候選任務", "-" * 42]
    for item in decision.evaluations:
        status = "ALLOW" if item.allowed else "DENY"
        lines.append(f"{item.task}: {item.total:.1f} [{status}]")
        for name, value in item.components.items():
            lines.append(f"  {name:<16} {value:+.1f}")
        if item.denied_reason:
            lines.append(f"  拒絕原因：{item.denied_reason}")
    return "\n".join(lines)


class ShopTitansAgent:
    def __init__(self, runtime_dir: str = "runtime_data") -> None:
        runtime = Path(runtime_dir)
        self.rules = RuleEngine()
        self.safety = SafetyPolicy()
        self.decisions = DecisionEngine(self.safety)
        self.blackbox = BlackBox(runtime / "blackbox")
        self.notebook = UnknownNotebook(runtime / "notebook")

    def run_once(self, state: WorldState, tasks: list[Task]) -> str:
        self.rules.evaluate(state)

        if state.is_unknown:
            report = self.notebook.record(state)
            self.blackbox.record(state, None, "UNKNOWN_STOP")
            return (
                "Agent 已安全停止。\n"
                f"原因：{state.unknown_reason}\n"
                f"報告：{report}"
            )

        decision = self.decisions.choose(state, tasks)
        self.blackbox.record(state, decision, "DECISION")
        return explain(decision)


def production_tasks() -> list[Task]:
    return [
        Task(
            "Collect Production",
            "COLLECT_PRODUCTION",
            lambda s: {
                "Ready": s.ready_count * 20.0,
                "Queue": 25.0 if s.queue_remaining == 0 else 10.0,
                "Guild": 15.0 if s.guild_objective in {
                    "CRAFT_ITEMS", "CRAFT_TIERS"
                } else 0.0,
                "Safety": 8.0,
            },
            condition=lambda s: s.ready_count > 0,
        ),
        Task(
            "Serve Customers",
            "SERVE_CUSTOMERS",
            lambda s: {
                "Customers": s.customer_count * 12.0,
                "Guild": 20.0 if s.guild_objective in {
                    "SELL_ITEMS", "SELL_TIERS"
                } else 0.0,
                "Inventory": 10.0,
                "Safety": 8.0,
            },
            condition=lambda s: s.customer_count > 0,
        ),
        Task(
            "Craft Recipe",
            "CRAFT_RECIPE",
            lambda s: {
                "Queue": 25.0,
                "Guild": 30.0 if s.guild_objective in {
                    "CRAFT_ITEMS", "CRAFT_TIERS"
                } else 0.0,
                "Collection": 20.0,
                "Material": 15.0,
                "Time": -5.0,
            },
            condition=lambda s: (
                s.queue_remaining is not None and s.queue_remaining > 0
            ),
        ),
        Task(
            "Diamond Rush",
            "DIAMOND_RUSH",
            lambda _s: {"Time": 999.0},
            uses_diamond=True,
        ),
    ]
