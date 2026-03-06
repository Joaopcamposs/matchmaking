from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BootstrapRequest(BaseModel):
    """Define os parâmetros para carga inicial do sistema."""

    player_total: int = Field(default=100, ge=1, le=1_000)


class RunMatchmakingRequest(BaseModel):
    """Define os parâmetros para execução de um ciclo de matchmaking."""

    players_per_match: int = Field(default=10, ge=2, le=100)
    match_duration_seconds: int = Field(default=300, ge=1, le=3_600)


class HealthResponse(BaseModel):
    """Representa o status básico da aplicação."""

    status: str


class SummaryResponse(BaseModel):
    """Representa um resumo persistido do simulador."""

    players: int
    npc_profiles: int
    matches: int
    actions: int


class RunMatchmakingResponse(BaseModel):
    """Representa o resultado de um ciclo executado pela API."""

    matches_created: int
    persisted_matches: int
    persisted_actions: int


class ActionFeedbackResponse(BaseModel):
    """Representa o feedback detalhado de uma ação persistida."""

    id: UUID
    match_id: UUID
    actor_id: UUID
    target_id: UUID | None
    action_type: str
    damage: int
    killed: bool
    revived: bool
    stunned: bool
    escaped: bool
    actor_karma_delta: float
    happened_at_second: int
    created_at: datetime


class MatchReportResponse(BaseModel):
    """Representa um relatório consolidado de uma partida."""

    match_id: UUID
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    player_count: int
    npc_count: int
    total_actions: int
    total_kills: int
    total_revives: int
    total_escapes: int
    total_stuns: int
    total_damage: int
    actions: list[ActionFeedbackResponse]


class MatchIdsResponse(BaseModel):
    """Representa a lista de identificadores de partidas persistidas."""

    match_ids: list[UUID]


class PlayerResponse(BaseModel):
    """Representa um jogador persistido exposto pela API."""

    id: UUID
    name: str
    karma: float
    kills: int
    deaths: int
    escapes: int
    revives: int


class CreatePlayerRequest(BaseModel):
    """Define os dados mínimos para criação de um jogador."""

    name: str = Field(min_length=1, max_length=120)
    karma: float = Field(default=0.0, ge=-100.0, le=100.0)


class UpdatePlayerRequest(BaseModel):
    """Define os dados editáveis de um jogador."""

    name: str = Field(min_length=1, max_length=120)
    karma: float = Field(ge=-100.0, le=100.0)
    kills: int = Field(ge=0)
    deaths: int = Field(ge=0)
    escapes: int = Field(ge=0)
    revives: int = Field(ge=0)


class NPCProfileResponse(BaseModel):
    """Representa um perfil de NPC exposto pela API."""

    id: UUID
    name: str
    difficulty: float
