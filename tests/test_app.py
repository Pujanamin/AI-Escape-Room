import pytest
import requests

from app import create_app
from app_v1 import app as v1_app


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key"})
    return app.test_client()


def test_initial_state_has_three_puzzles(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    assert response.json["progress"] == 0
    assert response.json["total"] == 3
    assert response.json["hints_remaining"] == 3


def test_correct_answer_advances_and_normalizes_punctuation(client):
    response = client.post("/api/message", json={"message": "Piano!"})
    assert response.status_code == 200
    assert response.json["progress"] == 1
    assert "drawer opens" in response.json["reply"]


def test_wrong_and_empty_answers_do_not_advance(client):
    wrong = client.post("/api/message", json={"message": "guitar"})
    empty = client.post("/api/message", json={"message": "  "})
    assert wrong.status_code == 200
    assert wrong.json["progress"] == 0
    assert empty.status_code == 400
    assert client.get("/api/state").json["progress"] == 0


def test_hint_limit_is_enforced(client):
    for _ in range(3):
        assert client.post("/api/hint").status_code == 200
    exhausted = client.post("/api/hint")
    assert exhausted.status_code == 409
    assert exhausted.json["error"] == "You have used all three hints."


def test_ai_failure_is_explicit_and_does_not_consume_hint(monkeypatch):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "AI_API_KEY": "test-key",
    })
    client = app.test_client()

    def fail_request(*args, **kwargs):
        raise requests.Timeout("test timeout")

    monkeypatch.setattr("app.requests.post", fail_request)
    response = client.post("/api/hint")
    assert response.status_code == 502
    assert "unavailable" in response.json["error"]
    assert client.get("/api/state").json["hints_remaining"] == 3


def test_game_sessions_are_isolated():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key"})
    first = app.test_client()
    second = app.test_client()
    first.post("/api/message", json={"message": "piano"})
    assert first.get("/api/state").json["progress"] == 1
    assert second.get("/api/state").json["progress"] == 0


def test_game_completes_and_restart_resets_state(client):
    for answer in ("piano", "clock", "towel"):
        response = client.post("/api/message", json={"message": answer})
        assert response.status_code == 200
    assert response.json["completed"] is True
    assert client.post("/api/message", json={"message": "piano"}).status_code == 409
    restarted = client.post("/api/restart")
    assert restarted.json["progress"] == 0
    assert restarted.json["completed"] is False
    assert restarted.json["messages"] == []


def test_malformed_and_oversized_input_are_rejected(client):
    malformed = client.post("/api/message", data="not-json", content_type="application/json")
    oversized = client.post("/api/message", json={"message": "x" * 501})
    assert malformed.status_code == 400
    assert oversized.status_code == 400
    assert client.get("/api/state").json["progress"] == 0


def test_v1_route_still_works(client):
    response = v1_app.test_client().post("/answer", json={"answer": "piano"})
    assert response.status_code == 200
    assert response.json["escaped"] is True
