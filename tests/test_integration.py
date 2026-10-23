from __future__ import annotations

import asyncio


def test_run_matchmaking_cycle_persists_matches_and_actions(service) -> None:
    """Valida o fluxo completo com matchmaking, simulação e persistência."""

    service.bootstrap(player_total=100)
    matches = asyncio.run(
        service.run_matchmaking_cycle(
            players_per_match=10,
            match_duration_seconds=30,
        )
    )

    assert len(matches) == 10

    match_repository = service._match_repository
    player_repository = service._player_repository

    assert match_repository.count_matches() == 10
    assert match_repository.count_actions() > 0
    assert len(player_repository.list_players_for_matchmaking()) == 100
