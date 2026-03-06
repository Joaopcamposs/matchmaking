from __future__ import annotations

from pathlib import Path

import pytest

from matchmaking.bootstrap import build_container
from matchmaking.infrastructure.database import DatabaseContext
from matchmaking.infrastructure.repositories import (
    SqlAlchemyMatchRepository,
    SqlAlchemyNPCRepository,
    SqlAlchemyPlayerRepository,
)


@pytest.fixture()
def sqlite_url(tmp_path: Path) -> str:
    """Fornece uma URL SQLite isolada para cada teste."""

    return f"sqlite:///{tmp_path / 'test_matchmaking.db'}"


@pytest.fixture()
def db_context(sqlite_url: str) -> DatabaseContext:
    """Cria um contexto de banco pronto para uso nos testes."""

    context = DatabaseContext(sqlite_url)
    context.create_schema()
    return context


@pytest.fixture()
def repositories(
    db_context: DatabaseContext,
) -> tuple[
    SqlAlchemyPlayerRepository,
    SqlAlchemyNPCRepository,
    SqlAlchemyMatchRepository,
]:
    """Retorna as implementações concretas de repositório para os testes."""

    return (
        SqlAlchemyPlayerRepository(db_context),
        SqlAlchemyNPCRepository(db_context),
        SqlAlchemyMatchRepository(db_context),
    )


@pytest.fixture()
def service(sqlite_url: str):
    """Monta o serviço principal apontando para um banco isolado."""

    return build_container(sqlite_url)
