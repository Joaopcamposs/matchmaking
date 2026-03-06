from __future__ import annotations

from dataclasses import asdict
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException

from matchmaking.api.dependencies import get_service
from matchmaking.api.schemas import (
    ActionFeedbackResponse,
    BootstrapRequest,
    CreatePlayerRequest,
    HealthResponse,
    MatchIdsResponse,
    MatchReportResponse,
    NPCProfileResponse,
    PlayerResponse,
    RunMatchmakingRequest,
    RunMatchmakingResponse,
    SummaryResponse,
    UpdatePlayerRequest,
)
from matchmaking.application.matchmaking_service import MatchmakingService
from matchmaking.domain.entities import Player


app = FastAPI(title="Matchmaking Simulator API", version="0.1.0")


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Expõe um endpoint simples de verificação de saúde."""

    return HealthResponse(status="ok")


@app.post("/bootstrap", response_model=SummaryResponse, tags=["system"])
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


@app.get("/summary", response_model=SummaryResponse, tags=["system"])
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


@app.get("/players", response_model=list[PlayerResponse], tags=["players"])
async def list_players(
    service: MatchmakingService = Depends(get_service),
) -> list[PlayerResponse]:
    """Lista todos os jogadores persistidos."""

    return [
        PlayerResponse(**asdict(player))
        for player in service._player_repository.list_players_for_matchmaking()
    ]


@app.get("/players/{player_id}", response_model=PlayerResponse, tags=["players"])
async def get_player(
    player_id: UUID,
    service: MatchmakingService = Depends(get_service),
) -> PlayerResponse:
    """Retorna um jogador específico."""

    player = service._player_repository.get_player(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerResponse(**asdict(player))


@app.post("/players", response_model=PlayerResponse, status_code=201, tags=["players"])
async def create_player(
    payload: CreatePlayerRequest,
    service: MatchmakingService = Depends(get_service),
) -> PlayerResponse:
    """Cria um novo jogador manualmente."""

    created = service._player_repository.create_player(
        Player(id=uuid4(), name=payload.name, karma=payload.karma)
    )
    return PlayerResponse(**asdict(created))


@app.put("/players/{player_id}", response_model=PlayerResponse, tags=["players"])
async def update_player(
    player_id: UUID,
    payload: UpdatePlayerRequest,
    service: MatchmakingService = Depends(get_service),
) -> PlayerResponse:
    """Atualiza um jogador existente."""

    updated = service._player_repository.update_player(
        Player(
            id=player_id,
            name=payload.name,
            karma=payload.karma,
            kills=payload.kills,
            deaths=payload.deaths,
            escapes=payload.escapes,
            revives=payload.revives,
        )
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerResponse(**asdict(updated))


@app.delete("/players/{player_id}", status_code=204, tags=["players"])
async def delete_player(
    player_id: UUID,
    service: MatchmakingService = Depends(get_service),
) -> None:
    """Remove um jogador existente."""

    if not service._player_repository.delete_player(player_id):
        raise HTTPException(status_code=404, detail="Player not found")


@app.get("/npc-profiles", response_model=list[NPCProfileResponse], tags=["npc"])
async def list_npc_profiles(
    service: MatchmakingService = Depends(get_service),
) -> list[NPCProfileResponse]:
    """Lista os perfis de NPC persistidos."""

    return [
        NPCProfileResponse(
            id=profile.id,
            name=profile.name,
            difficulty=profile.difficulty,
        )
        for profile in service._npc_repository.list_profiles()
    ]


@app.post(
    "/matchmaking/run",
    response_model=RunMatchmakingResponse,
    tags=["matchmaking"],
)
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


@app.get("/actions", response_model=list[ActionFeedbackResponse], tags=["actions"])
async def list_actions(
    service: MatchmakingService = Depends(get_service),
) -> list[ActionFeedbackResponse]:
    """Retorna feedback detalhado de todas as ações persistidas."""

    return [
        ActionFeedbackResponse(**action)
        for action in service._match_repository.list_actions()
    ]


@app.get("/matches/ids", response_model=MatchIdsResponse, tags=["matches"])
async def list_match_ids(
    service: MatchmakingService = Depends(get_service),
) -> MatchIdsResponse:
    """Retorna os identificadores de todas as partidas persistidas."""

    return MatchIdsResponse(match_ids=service._match_repository.get_match_ids())


@app.get(
    "/matches/{match_id}/report",
    response_model=MatchReportResponse,
    tags=["matches"],
)
async def get_match_report(
    match_id: UUID,
    service: MatchmakingService = Depends(get_service),
) -> MatchReportResponse:
    """Retorna um relatório detalhado de tudo que ocorreu em uma partida."""

    report = service._match_repository.get_match_report(match_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return MatchReportResponse(**report)
