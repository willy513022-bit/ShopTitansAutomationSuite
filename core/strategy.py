from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

class StrategyMode(StrEnum):
    DAILY='daily'; EVENT='event'; COLLECTION='collection'; MONEY='money'; CUSTOM='custom'
class LostCityMode(StrEnum):
    BALANCED='balanced'; FULL='full'; CUSTOM='custom'; DISABLED='disabled'

@dataclass(frozen=True, slots=True)
class Strategy:
    mode: StrategyMode = StrategyMode.DAILY
    event_priority_enabled: bool = False
    lost_city_mode: LostCityMode = LostCityMode.BALANCED
    reserve_collection_parties: int = 1
    reserve_regular_quest_parties: int = 0
    feature_flags: Mapping[str,bool] = field(default_factory=lambda:{'collection':True,'lostcity':True,'craft':True,'customer':True,'market':True,'kingscaprice':True})
    planner_modifiers: Mapping[str,float] = field(default_factory=dict)
    action_modifiers: Mapping[str,float] = field(default_factory=dict)
    confidence_weight: float = 0.0
    def __post_init__(self):
        if self.reserve_collection_parties < 0 or self.reserve_regular_quest_parties < 0: raise ValueError('party reserves must not be negative')
        if self.confidence_weight < 0: raise ValueError('confidence_weight must not be negative')
        object.__setattr__(self,'feature_flags',MappingProxyType(dict(self.feature_flags)))
        object.__setattr__(self,'planner_modifiers',MappingProxyType(dict(self.planner_modifiers)))
        object.__setattr__(self,'action_modifiers',MappingProxyType(dict(self.action_modifiers)))
    def is_enabled(self, planner_name:str)->bool:
        return self.feature_flags.get(planner_name.strip().lower(), True)
    def effective_collection_reserve(self)->int:
        return 0 if self.lost_city_mode == LostCityMode.FULL else self.reserve_collection_parties
