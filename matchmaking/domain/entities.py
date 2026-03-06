from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import UUID, uuid4

from matchmaking.domain.enums import ActionType


@dataclass(slots=True)
class Player:
    """Representa um jogador persistido e elegível para matchmaking."""

    id: UUID
    name: str
    karma: float
    kills: int = 0
    deaths: int = 0
    escapes: int = 0
    revives: int = 0


@dataclass(slots=True)
class NPCProfile:
    """Representa um tipo fixo de NPC disponível para partidas."""

    id: UUID
    name: str
    difficulty: float


@dataclass(slots=True)
class MatchParticipant:
    """Representa um participante em tempo de execução dentro de uma partida."""

    id: UUID
    name: str
    is_npc: bool
    karma: float = 0.0
    difficulty: float = 0.0
    life: int = 100
    alive: bool = True
    stunned: bool = False
    stunned_life: int = 0
    escaped: bool = False
    kills: int = 0
    deaths: int = 0
    revives: int = 0

    def can_receive_damage(self) -> bool:
        """Indica se o participante ainda pode sofrer dano direto."""

        return self.alive and not self.escaped


@dataclass(slots=True)
class MatchAction:
    """Representa um evento ocorrido durante a simulação da partida."""

    id: UUID
    match_id: UUID
    actor_id: UUID
    target_id: UUID | None
    action_type: ActionType
    damage: int
    killed: bool
    revived: bool
    stunned: bool
    escaped: bool
    actor_karma_delta: float
    happened_at_second: int
    created_at: datetime


@dataclass(slots=True)
class Match:
    """Representa o agregado principal da partida simulada."""

    id: UUID
    players: list[MatchParticipant]
    npcs: list[MatchParticipant]
    duration_seconds: int
    started_at: datetime
    ended_at: datetime | None = None
    actions: list[MatchAction] = field(default_factory=list)

    def living_players(self) -> list[MatchParticipant]:
        """Retorna jogadores ainda ativos na partida."""

        return [
            player for player in self.players if player.alive and not player.escaped
        ]

    def living_npcs(self) -> list[MatchParticipant]:
        """Retorna NPCs ainda vivos na partida."""

        return [npc for npc in self.npcs if npc.alive]

    def active_participants(self) -> list[MatchParticipant]:
        """Retorna todos os participantes ativos na partida."""

        return self.living_players() + self.living_npcs()


def build_player_participant(player: Player) -> MatchParticipant:
    """Converte um jogador persistido em participante de partida."""

    return MatchParticipant(
        id=player.id,
        name=player.name,
        is_npc=False,
        karma=player.karma,
    )


def build_npc_participant(profile: NPCProfile) -> MatchParticipant:
    """Converte um perfil de NPC em participante de partida."""

    return MatchParticipant(
        id=profile.id,
        name=profile.name,
        is_npc=True,
        difficulty=profile.difficulty,
        life=60,
    )


def new_match_action(
    *,
    match_id: UUID,
    actor_id: UUID,
    target_id: UUID | None,
    action_type: ActionType,
    damage: int = 0,
    killed: bool = False,
    revived: bool = False,
    stunned: bool = False,
    escaped: bool = False,
    actor_karma_delta: float = 0.0,
    happened_at_second: int,
) -> MatchAction:
    """Cria uma ação de partida com metadados padronizados."""

    return MatchAction(
        id=uuid4(),
        match_id=match_id,
        actor_id=actor_id,
        target_id=target_id,
        action_type=action_type,
        damage=damage,
        killed=killed,
        revived=revived,
        stunned=stunned,
        escaped=escaped,
        actor_karma_delta=actor_karma_delta,
        happened_at_second=happened_at_second,
        created_at=datetime.now(UTC),
    )
