from __future__ import annotations

from fastapi.testclient import TestClient

from matchmaking.api.app import app
from matchmaking.api.dependencies import get_service
from matchmaking.bootstrap import build_container


def test_api_endpoints(sqlite_url: str) -> None:
    """Valida o fluxo HTTP principal da aplicação."""

    app.dependency_overrides[get_service] = lambda: build_container(sqlite_url)
    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    bootstrap_response = client.post("/bootstrap", json={"player_total": 100})
    assert bootstrap_response.status_code == 200
    assert bootstrap_response.json()["players"] == 100
    assert bootstrap_response.json()["npc_profiles"] == 10

    run_response = client.post(
        "/matchmaking/run",
        json={"players_per_match": 10, "match_duration_seconds": 20},
    )
    assert run_response.status_code == 200
    assert run_response.json()["matches_created"] == 10

    summary_response = client.get("/summary")
    assert summary_response.status_code == 200
    payload = summary_response.json()
    assert payload["players"] == 100
    assert payload["matches"] == 10
    assert payload["actions"] > 0

    app.dependency_overrides.clear()
