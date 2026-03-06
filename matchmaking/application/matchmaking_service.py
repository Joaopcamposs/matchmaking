from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Iterable
from math import ceil
from random import Random

from matchmaking.application.interfaces import (
    MatchRepository,
    NPCRepository,
    PlayerRepository,
)
from matchmaking.application.simulation import MatchSimulator
from matchmaking.domain.entities import Match, NPCProfile, Player
from matchmaking.domain.services import MatchFactory


class MatchmakingService:
    """Orquestra o agrupamento, processamento paralelo e consolidação das partidas."""

    def __init__(
        self,
        player_repository: PlayerRepository,
        npc_repository: NPCRepository,
        match_repository: MatchRepository,
        simulator: MatchSimulator,
        factory: MatchFactory,
        random_seed: int | None = None,
    ) -> None:
        """Configura as dependências necessárias para executar o fluxo."""

        self._player_repository = player_repository
        self._npc_repository = npc_repository
        self._match_repository = match_repository
        self._simulator = simulator
        self._factory = factory
        self._random = Random(random_seed)

    def bootstrap(self, player_total: int = 100) -> None:
        """Garante massa inicial de jogadores e NPCs no banco."""

        players = self._player_repository.list_players_for_matchmaking()
        if not players:
            self._player_repository.seed_players(player_total)
        profiles = self._npc_repository.list_profiles()
        if not profiles:
            self._npc_repository.seed_default_profiles()

    async def run_matchmaking_cycle(
        self,
        players_per_match: int = 10,
        match_duration_seconds: int = 300,
    ) -> list[Match]:
        """Executa um ciclo completo de matchmaking e simulação de forma concorrente."""

        players = self._player_repository.list_players_for_matchmaking()
        npc_profiles = self._npc_repository.list_profiles()
        groups = self._build_groups(players, players_per_match)
        if not groups:
            return []
        selected_npcs = self._split_npcs_for_groups(npc_profiles, len(groups))

        tasks = [
            asyncio.to_thread(
                self._run_single_match,
                group,
                npc_group,
                match_duration_seconds,
            )
            for group, npc_group in zip(groups, selected_npcs, strict=True)
        ]
        matches = await asyncio.gather(*tasks)
        self._consolidate_players(matches)
        return list(matches)

    def _run_single_match(
        self,
        players: list[Player],
        npc_profiles: list[NPCProfile],
        match_duration_seconds: int,
    ) -> Match:
        """Processa uma partida isolada em uma thread dedicada."""

        match = self._factory.create(players, npc_profiles, match_duration_seconds)
        match = self._simulator.simulate(match)
        self._match_repository.save_match(match)
        return match

    def _build_groups(
        self, players: list[Player], players_per_match: int
    ) -> list[list[Player]]:
        """Agrupa jogadores por faixas de karma com ruído aleatório controlado."""

        ordered_players = sorted(players, key=lambda item: item.karma, reverse=True)
        for index in range(
            0, max(len(ordered_players) - 1, 0), max(1, players_per_match // 3)
        ):
            if self._random.random() < 0.25:
                swap_index = min(
                    len(ordered_players) - 1,
                    index + self._random.randint(1, max(1, players_per_match // 2)),
                )
                ordered_players[index], ordered_players[swap_index] = (
                    ordered_players[swap_index],
                    ordered_players[index],
                )
        return [
            ordered_players[index : index + players_per_match]
            for index in range(0, len(ordered_players), players_per_match)
            if ordered_players[index : index + players_per_match]
        ]

    @staticmethod
    def _split_npcs_for_groups(
        npc_profiles: list[NPCProfile], group_count: int
    ) -> list[list[NPCProfile]]:
        """Distribui NPCs entre as partidas com repetição de tipos quando necessário."""

        if group_count == 0:
            return []
        if not npc_profiles:
            return [[] for _ in range(group_count)]
        npcs_per_group = max(1, ceil(len(npc_profiles) / group_count))
        groups: list[list[NPCProfile]] = []
        cursor = 0
        for _ in range(group_count):
            bucket: list[NPCProfile] = []
            for _ in range(npcs_per_group):
                bucket.append(npc_profiles[cursor % len(npc_profiles)])
                cursor += 1
            groups.append(bucket)
        return groups

    def _consolidate_players(self, matches: Iterable[Match]) -> None:
        """Consolida os resultados das partidas no estado persistido dos jogadores."""

        persisted = {
            player.id: player
            for player in self._player_repository.list_players_for_matchmaking()
        }
        aggregate_kills = defaultdict(int)
        aggregate_deaths = defaultdict(int)
        aggregate_escapes = defaultdict(int)
        aggregate_revives = defaultdict(int)
        aggregate_karma = defaultdict(float)

        for match in matches:
            for player in match.players:
                aggregate_kills[player.id] += player.kills
                aggregate_deaths[player.id] += player.deaths
                aggregate_escapes[player.id] += 1 if player.escaped else 0
                aggregate_revives[player.id] += player.revives
                aggregate_karma[player.id] += player.karma

        for player_id, persisted_player in persisted.items():
            contributed_karma = aggregate_karma.get(player_id)
            if contributed_karma:
                persisted_player.karma = round(contributed_karma, 2)
            persisted_player.kills += aggregate_kills[player_id]
            persisted_player.deaths += aggregate_deaths[player_id]
            persisted_player.escapes += aggregate_escapes[player_id]
            persisted_player.revives += aggregate_revives[player_id]

        self._player_repository.save_players(list(persisted.values()))
