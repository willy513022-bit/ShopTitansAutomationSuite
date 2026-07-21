from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class LostCityAction(str, Enum):
    CLAIM_MILESTONE = "claim_milestone"
    START_BOSS_QUEST = "start_boss_quest"
    START_REPEATABLE_QUEST = "start_repeatable_quest"
    WAIT_FOR_PARTY = "wait_for_party"
    WAIT_FOR_EVENT = "wait_for_event"
    EVENT_COMPLETE = "event_complete"

class BossQuestState(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED_THIS_EVENT = "completed_this_event"

@dataclass(frozen=True)
class LostCityParty:
    party_id: str
    face_status: str
    available: bool = True
    reserved_for_collection: bool = False
    reserved_for_hero: bool = False
    estimated_success_score: int = 0

@dataclass(frozen=True)
class LostCityBossQuest:
    quest_id: str
    name: str
    state: BossQuestState
    expected_gold: int
    expected_key_chance_score: int
    parties: tuple[LostCityParty, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class LostCityRepeatableQuest:
    quest_id: str
    name: str
    expected_gold: int
    duration_seconds: int
    parties: tuple[LostCityParty, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class LostCityMilestone:
    milestone_id: str
    required_gold: int
    reward_name: str
    claimable: bool = False
    claimed: bool = False

@dataclass(frozen=True)
class LostCityState:
    active: bool
    current_gold: int
    event_seconds_remaining: int
    boss_quests: tuple[LostCityBossQuest, ...] = field(default_factory=tuple)
    repeatable_quests: tuple[LostCityRepeatableQuest, ...] = field(default_factory=tuple)
    milestones: tuple[LostCityMilestone, ...] = field(default_factory=tuple)
