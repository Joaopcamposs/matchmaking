from __future__ import annotations

import uvicorn


def run() -> None:
    """Inicializa o servidor HTTP da aplicação."""

    uvicorn.run("matchmaking.api.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
