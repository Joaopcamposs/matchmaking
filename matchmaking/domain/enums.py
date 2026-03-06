from enum import Enum


class ActionType(str, Enum):
    """Define os tipos de ação válidos dentro de uma partida."""

    PLAYER_ATTACK = "player_attack"
    NPC_ATTACK = "npc_attack"
    REVIVE = "revive"
    ESCAPE = "escape"
    STUN_TICK = "stun_tick"


class ParticipantType(str, Enum):
    """Define o tipo de participante da partida."""

    PLAYER = "player"
    NPC = "npc"
