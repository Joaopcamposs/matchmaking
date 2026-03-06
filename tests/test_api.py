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

    players_response = client.get("/players")
    assert players_response.status_code == 200
    players_payload = players_response.json()
    assert len(players_payload) == 100

    create_player_response = client.post(
        "/players",
        json={"name": "Custom Player", "karma": 1.5},
    )
    assert create_player_response.status_code == 201
    created_player = create_player_response.json()
    created_player_id = created_player["id"]
    assert created_player["name"] == "Custom Player"

    get_player_response = client.get(f"/players/{created_player_id}")
    assert get_player_response.status_code == 200
    assert get_player_response.json()["id"] == created_player_id

    update_player_response = client.put(
        f"/players/{created_player_id}",
        json={
            "name": "Updated Player",
            "karma": 2.0,
            "kills": 3,
            "deaths": 1,
            "escapes": 0,
            "revives": 2,
        },
    )
    assert update_player_response.status_code == 200
    assert update_player_response.json()["name"] == "Updated Player"
    assert update_player_response.json()["kills"] == 3

    npc_response = client.get("/npc-profiles")
    assert npc_response.status_code == 200
    assert len(npc_response.json()) == 10

    run_response = client.post(
        "/matchmaking/run",
        json={"players_per_match": 10, "match_duration_seconds": 20},
    )
    assert run_response.status_code == 200
    assert run_response.json()["matches_created"] == 11

    actions_response = client.get("/actions")
    assert actions_response.status_code == 200
    actions_payload = actions_response.json()
    assert len(actions_payload) > 0
    assert "action_type" in actions_payload[0]
    assert "match_id" in actions_payload[0]

    match_ids_response = client.get("/matches/ids")
    assert match_ids_response.status_code == 200
    match_ids_payload = match_ids_response.json()["match_ids"]
    assert len(match_ids_payload) == 11

    summary_response = client.get("/summary")
    assert summary_response.status_code == 200
    payload = summary_response.json()
    assert payload["players"] == 101
    assert payload["matches"] == 11
    assert payload["actions"] > 0

    first_match_id = match_ids_payload[0]
    report_response = client.get(f"/matches/{first_match_id}/report")
    assert report_response.status_code == 200
    report_payload = report_response.json()
    assert report_payload["match_id"] == first_match_id
    assert report_payload["total_actions"] > 0
    assert len(report_payload["actions"]) > 0

    missing_match_response = client.get(
        "/matches/00000000-0000-0000-0000-000000000000/report"
    )
    assert missing_match_response.status_code == 404

    delete_player_response = client.delete(f"/players/{created_player_id}")
    assert delete_player_response.status_code == 204

    missing_player_response = client.get(f"/players/{created_player_id}")
    assert missing_player_response.status_code == 404

    app.dependency_overrides.clear()
