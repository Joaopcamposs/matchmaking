from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Uuid


@dataclass
class Player:
    id: Uuid
    name: str
    karma: float
    kills: int
    deaths: int


@dataclass
class NPC:
    id: Uuid
    name: str
    difficulty: float
    kills: int
    deaths: int


@dataclass
class Action:
    id: Uuid
    match_id: Uuid
    actor_id: Uuid
    target_id: Uuid
    life: int
    damage: int
    killed: bool
    relived: bool
    stunned: bool
    stunned_life: int
    escaped: bool
    act_karma: float
    timestamp: datetime


@dataclass
class MatchStats:
    id: Uuid
    actions: list[Action]
    kills: int
    deaths: int
    escapeds: int


@dataclass
class Match:
    id: Uuid
    players: list[Player]
    stats: MatchStats
    started_at: datetime
    ended_at: datetime

