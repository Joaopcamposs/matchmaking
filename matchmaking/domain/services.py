from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from matchmaking.domain.entities import (
    Match,
    MatchParticipant,
    NPCProfile,
    Player,
    build_npc_participant,
    build_player_participant,
)


class MatchFactory:
    """Cria agregados de partida a partir de jogadores e NPCs."""

    @staticmethod
    def create(
        players: list[Player],
        npc_profiles: list[NPCProfile],
        duration_seconds: int,
    ) -> Match:
        """Monta uma partida pronta para simulação."""

        participants: list[MatchParticipant] = [
            build_player_participant(player) for player in players
        ]
        npcs = [build_npc_participant(profile) for profile in npc_profiles]
        return Match(
            id=uuid4(),
            players=participants,
            npcs=npcs,
            duration_seconds=duration_seconds,
            started_at=datetime.now(UTC),
        )
