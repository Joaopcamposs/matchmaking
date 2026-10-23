from __future__ import annotations

from matchmaking.bootstrap import build_container


def get_service():
    """Fornece a instância principal da aplicação para as rotas."""

    return build_container()
