from __future__ import annotations

from datetime import datetime, UTC
from random import Random
from uuid import uuid4

from matchmaking.application.simulation import MatchSimulator
from matchmaking.domain.entities import Match, MatchParticipant
from matchmaking.domain.enums import ActionType


def test_player_kill_reduces_karma() -> None:
    """Valida que matar outro jogador reduz o karma do atacante."""

    simulator = MatchSimulator()
    actor = MatchParticipant(id=uuid4(), name="Hero", is_npc=False, karma=-1.0)
    target = MatchParticipant(
        id=uuid4(),
        name="Target",
        is_npc=False,
        karma=0.2,
        life=10,
        stunned=True,
        stunned_life=1,
    )
    match = Match(
        id=uuid4(),
        players=[actor, target],
        npcs=[],
        duration_seconds=10,
        started_at=datetime.now(UTC),
    )

    simulator._process_player_attack(match, actor, 0, Random(1))

    assert actor.karma < -1.0
    assert target.alive is False
    assert any(action.killed for action in match.actions)


def test_npc_can_only_stun_player() -> None:
    """Garante que NPCs atordoam jogadores, mas não finalizam o abate direto."""

    simulator = MatchSimulator()
    npc = MatchParticipant(id=uuid4(), name="NPC", is_npc=True, difficulty=1.5)
    player = MatchParticipant(id=uuid4(), name="Player", is_npc=False, life=5)
    match = Match(
        id=uuid4(),
        players=[player],
        npcs=[npc],
        duration_seconds=10,
        started_at=datetime.now(UTC),
    )

    simulator._process_npc_turn(match, npc, 0, Random(2))

    assert player.stunned is True
    assert player.alive is True
    assert match.actions[-1].action_type is ActionType.NPC_ATTACK


def test_npcs_spawn_at_different_times() -> None:
    """Garante que múltiplos NPCs entram em momentos diferentes."""

    simulator = MatchSimulator()
    player = MatchParticipant(id=uuid4(), name="Player", is_npc=False, karma=-0.5)
    npcs = [
        MatchParticipant(
            id=uuid4(),
            name=f"NPC {index}",
            is_npc=True,
            difficulty=1.0 + index,
            life=60,
            spawned=False,
        )
        for index in range(3)
    ]
    match = Match(
        id=uuid4(),
        players=[player],
        npcs=npcs,
        duration_seconds=12,
        started_at=datetime.now(UTC),
    )

    simulator.simulate(match)

    spawn_actions = [
        action for action in match.actions if action.action_type is ActionType.NPC_SPAWN
    ]
    assert len(spawn_actions) == 3
    assert len({action.happened_at_second for action in spawn_actions}) > 1


def test_all_players_finish_dead_or_escaped() -> None:
    """Garante que a soma de mortos e fugitivos fecha o total inicial."""

    simulator = MatchSimulator()
    players = [
        MatchParticipant(id=uuid4(), name=f"Player {index}", is_npc=False)
        for index in range(4)
    ]
    match = Match(
        id=uuid4(),
        players=players,
        npcs=[],
        duration_seconds=1,
        started_at=datetime.now(UTC),
    )

    simulator.simulate(match)

    total_finished = sum(player.escaped or not player.alive for player in match.players)
    assert total_finished == len(match.players)
