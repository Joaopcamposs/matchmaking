from __future__ import annotations


def test_seed_players_and_npcs(repositories) -> None:
    """Valida a carga inicial de jogadores e perfis de NPC."""

    player_repository, npc_repository, _ = repositories

    players = player_repository.seed_players(100)
    npcs = npc_repository.seed_default_profiles()

    assert len(players) == 100
    assert len(npcs) == 10
    assert len(player_repository.list_players_for_matchmaking()) == 100
    assert len(npc_repository.list_profiles()) == 10
