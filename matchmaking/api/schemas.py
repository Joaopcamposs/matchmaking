from __future__ import annotations

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
