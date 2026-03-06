from __future__ import annotations

from typing import Protocol
from uuid import UUID

from matchmaking.domain.entities import Match, NPCProfile, Player


class PlayerRepository(Protocol):
    """Define o contrato de persistência para jogadores."""

    def list_players_for_matchmaking(self) -> list[Player]: ...

    def save_players(self, players: list[Player]) -> None: ...

    def seed_players(self, total: int) -> list[Player]: ...


class NPCRepository(Protocol):
    """Define o contrato de persistência para NPCs."""

    def list_profiles(self) -> list[NPCProfile]: ...

    def seed_default_profiles(self) -> list[NPCProfile]: ...


class MatchRepository(Protocol):
    """Define o contrato de persistência para partidas simuladas."""

    def save_match(self, match: Match) -> None: ...

    def count_matches(self) -> int: ...

    def count_actions(self) -> int: ...

    def get_match_ids(self) -> list[UUID]: ...
