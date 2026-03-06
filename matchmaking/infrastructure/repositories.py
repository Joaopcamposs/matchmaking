from __future__ import annotations

from math import sin
from uuid import UUID, uuid4

from sqlalchemy import func, select

from matchmaking.domain.entities import Match, MatchAction, NPCProfile, Player
from matchmaking.infrastructure.database import DatabaseContext
from matchmaking.infrastructure.orm import (
    MatchActionModel,
    MatchModel,
    NPCProfileModel,
    PlayerModel,
)


class SqlAlchemyPlayerRepository:
    """Implementa persistência de jogadores em SQLite."""

    def __init__(self, context: DatabaseContext) -> None:
        """Recebe o contexto de banco compartilhado pela aplicação."""

        self._context = context

    def list_players_for_matchmaking(self) -> list[Player]:
        """Retorna os jogadores mais recentes ordenados por karma."""

        with self._context.session_factory() as session:
            rows = session.scalars(
                select(PlayerModel).order_by(
                    PlayerModel.karma.desc(), PlayerModel.name.asc()
                )
            ).all()
        return [self._to_entity(row) for row in rows]

    def save_players(self, players: list[Player]) -> None:
        """Persiste o estado consolidado dos jogadores após as partidas."""

        with self._context.session_factory() as session:
            for player in players:
                row = session.get(PlayerModel, str(player.id))
                if row is None:
                    row = PlayerModel(id=str(player.id), name=player.name)
                    session.add(row)
                row.name = player.name
                row.karma = player.karma
                row.kills = player.kills
                row.deaths = player.deaths
                row.escapes = player.escapes
                row.revives = player.revives
            session.commit()

    def seed_players(self, total: int) -> list[Player]:
        """Gera jogadores iniciais com distribuição variada de karma."""

        players = [
            Player(
                id=uuid4(),
                name=f"Player {index + 1}",
                karma=round(sin(index / 7) * 1.8, 2),
            )
            for index in range(total)
        ]
        self.save_players(players)
        return players

    @staticmethod
    def _to_entity(row: PlayerModel) -> Player:
        """Converte o modelo ORM em entidade de domínio."""

        return Player(
            id=UUID(row.id),
            name=row.name,
            karma=row.karma,
            kills=row.kills,
            deaths=row.deaths,
            escapes=row.escapes,
            revives=row.revives,
        )


class SqlAlchemyNPCRepository:
    """Implementa persistência dos perfis fixos de NPC."""

    def __init__(self, context: DatabaseContext) -> None:
        """Recebe o contexto de banco compartilhado pela aplicação."""

        self._context = context

    def list_profiles(self) -> list[NPCProfile]:
        """Lista todos os perfis de NPC cadastrados."""

        with self._context.session_factory() as session:
            rows = session.scalars(
                select(NPCProfileModel).order_by(NPCProfileModel.name.asc())
            ).all()
        return [
            NPCProfile(id=UUID(row.id), name=row.name, difficulty=row.difficulty)
            for row in rows
        ]

    def seed_default_profiles(self) -> list[NPCProfile]:
        """Cria os 10 tipos fixos de NPC previstos pelo requisito."""

        with self._context.session_factory() as session:
            existing = session.scalar(select(func.count()).select_from(NPCProfileModel))
            if existing and existing > 0:
                rows = session.scalars(
                    select(NPCProfileModel).order_by(NPCProfileModel.name.asc())
                ).all()
                return [
                    NPCProfile(
                        id=UUID(row.id), name=row.name, difficulty=row.difficulty
                    )
                    for row in rows
                ]

            profiles: list[NPCProfile] = []
            for index in range(10):
                profile = NPCProfile(
                    id=uuid4(),
                    name=f"NPC Type {index + 1}",
                    difficulty=round(0.5 + index * 0.15, 2),
                )
                profiles.append(profile)
                session.add(
                    NPCProfileModel(
                        id=str(profile.id),
                        name=profile.name,
                        difficulty=profile.difficulty,
                    )
                )
            session.commit()
        return profiles


class SqlAlchemyMatchRepository:
    """Implementa persistência de partidas e eventos."""

    def __init__(self, context: DatabaseContext) -> None:
        """Recebe o contexto de banco compartilhado pela aplicação."""

        self._context = context

    def save_match(self, match: Match) -> None:
        """Persiste uma partida e todas as ações produzidas na simulação."""

        with self._context.session_factory() as session:
            session.add(
                MatchModel(
                    id=str(match.id),
                    started_at=match.started_at,
                    ended_at=match.ended_at or match.started_at,
                    duration_seconds=match.duration_seconds,
                    player_count=len(match.players),
                    npc_count=len(match.npcs),
                )
            )
            for action in match.actions:
                session.add(self._to_action_model(action))
            session.commit()

    def count_matches(self) -> int:
        """Conta quantas partidas existem no banco."""

        with self._context.session_factory() as session:
            return int(
                session.scalar(select(func.count()).select_from(MatchModel)) or 0
            )

    def count_actions(self) -> int:
        """Conta quantas ações foram persistidas."""

        with self._context.session_factory() as session:
            return int(
                session.scalar(select(func.count()).select_from(MatchActionModel)) or 0
            )

    def get_match_ids(self) -> list[UUID]:
        """Retorna os identificadores de partidas persistidas."""

        with self._context.session_factory() as session:
            values = session.scalars(
                select(MatchModel.id).order_by(MatchModel.started_at.asc())
            ).all()
        return [UUID(value) for value in values]

    @staticmethod
    def _to_action_model(action: MatchAction) -> MatchActionModel:
        """Converte uma entidade de ação para o modelo ORM."""

        return MatchActionModel(
            id=str(action.id),
            match_id=str(action.match_id),
            actor_id=str(action.actor_id),
            target_id=str(action.target_id) if action.target_id else None,
            action_type=action.action_type.value,
            damage=action.damage,
            killed=action.killed,
            revived=action.revived,
            stunned=action.stunned,
            escaped=action.escaped,
            actor_karma_delta=action.actor_karma_delta,
            happened_at_second=action.happened_at_second,
            created_at=action.created_at,
        )
