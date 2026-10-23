from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from matchmaking.infrastructure.database import Base


class PlayerModel(Base):
    """Modelo ORM para jogadores."""

    __tablename__ = "players"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    karma: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    kills: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    escapes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revives: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class NPCProfileModel(Base):
    """Modelo ORM para tipos fixos de NPC."""

    __tablename__ = "npc_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, nullable=False)


class MatchModel(Base):
    """Modelo ORM para partidas simuladas."""

    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    player_count: Mapped[int] = mapped_column(Integer, nullable=False)
    npc_count: Mapped[int] = mapped_column(Integer, nullable=False)


class MatchActionModel(Base):
    """Modelo ORM para ações geradas nas partidas."""

    __tablename__ = "match_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    match_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("matches.id"), nullable=False, index=True
    )
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action_type: Mapped[str] = mapped_column(String(40), nullable=False)
    damage: Mapped[int] = mapped_column(Integer, nullable=False)
    killed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    revived: Mapped[bool] = mapped_column(Boolean, nullable=False)
    stunned: Mapped[bool] = mapped_column(Boolean, nullable=False)
    escaped: Mapped[bool] = mapped_column(Boolean, nullable=False)
    actor_karma_delta: Mapped[float] = mapped_column(Float, nullable=False)
    happened_at_second: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
