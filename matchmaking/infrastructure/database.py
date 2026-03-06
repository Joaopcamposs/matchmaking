from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base declarativa para os modelos ORM."""


class DatabaseContext:
    """Centraliza engine, sessão e inicialização do banco SQLite."""

    def __init__(self, database_url: str = "sqlite:///matchmaking.db") -> None:
        """Configura a conexão com SQLite e a fábrica de sessões."""

        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            future=True,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        """Cria todas as tabelas necessárias para a aplicação."""

        from matchmaking.infrastructure.orm import Base as OrmBase

        OrmBase.metadata.create_all(self.engine)

    @staticmethod
    def default_sqlite_file() -> Path:
        """Retorna o caminho padrão do banco local."""

        return Path("matchmaking.db")
