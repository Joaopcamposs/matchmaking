from __future__ import annotations

from fastapi import Depends, FastAPI

from matchmaking.api.dependencies import get_service
from matchmaking.api.schemas import (
    BootstrapRequest,
    HealthResponse,
    RunMatchmakingRequest,
    RunMatchmakingResponse,
    SummaryResponse,
)
from matchmaking.application.matchmaking_service import MatchmakingService


app = FastAPI(title="Matchmaking Simulator API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Expõe um endpoint simples de verificação de saúde."""

    return HealthResponse(status="ok")


@app.post("/bootstrap", response_model=SummaryResponse)
async def bootstrap(
    payload: BootstrapRequest,
    service: MatchmakingService = Depends(get_service),
) -> SummaryResponse:
    """Inicializa a base de jogadores e NPCs quando necessário."""

    service.bootstrap(player_total=payload.player_total)
    return SummaryResponse(
        players=len(service._player_repository.list_players_for_matchmaking()),
        npc_profiles=len(service._npc_repository.list_profiles()),
        matches=service._match_repository.count_matches(),
        actions=service._match_repository.count_actions(),
    )


@app.post("/matchmaking/run", response_model=RunMatchmakingResponse)
async def run_matchmaking(
    payload: RunMatchmakingRequest,
    service: MatchmakingService = Depends(get_service),
) -> RunMatchmakingResponse:
    """Executa um ciclo de matchmaking e retorna o resumo persistido."""

    service.bootstrap(player_total=100)
    matches = await service.run_matchmaking_cycle(
        players_per_match=payload.players_per_match,
        match_duration_seconds=payload.match_duration_seconds,
    )
    return RunMatchmakingResponse(
        matches_created=len(matches),
        persisted_matches=service._match_repository.count_matches(),
        persisted_actions=service._match_repository.count_actions(),
    )


@app.get("/summary", response_model=SummaryResponse)
async def summary(
    service: MatchmakingService = Depends(get_service),
) -> SummaryResponse:
    """Retorna um resumo do estado persistido da aplicação."""

    return SummaryResponse(
        players=len(service._player_repository.list_players_for_matchmaking()),
        npc_profiles=len(service._npc_repository.list_profiles()),
        matches=service._match_repository.count_matches(),
        actions=service._match_repository.count_actions(),
    )
