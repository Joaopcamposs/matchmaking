from __future__ import annotations

from matchmaking.application.matchmaking_service import MatchmakingService
from matchmaking.application.simulation import MatchSimulator
from matchmaking.domain.services import MatchFactory
from matchmaking.infrastructure.database import DatabaseContext
from matchmaking.infrastructure.repositories import (
    SqlAlchemyMatchRepository,
    SqlAlchemyNPCRepository,
    SqlAlchemyPlayerRepository,
)


def build_container(
    database_url: str = "sqlite:///matchmaking.db",
) -> MatchmakingService:
    """Monta as dependências principais da aplicação."""

    context = DatabaseContext(database_url=database_url)
    context.create_schema()
    player_repository = SqlAlchemyPlayerRepository(context)
    npc_repository = SqlAlchemyNPCRepository(context)
    match_repository = SqlAlchemyMatchRepository(context)
    simulator = MatchSimulator()
    factory = MatchFactory()
    return MatchmakingService(
        player_repository=player_repository,
        npc_repository=npc_repository,
        match_repository=match_repository,
        simulator=simulator,
        factory=factory,
    )
