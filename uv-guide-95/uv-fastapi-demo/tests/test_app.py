from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_read_delete() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/tasks", json={"title": "learn uv"})
        assert created.status_code == 201
        assert created.json() == {"id": 1, "title": "learn uv", "done": False}

        found = client.get("/tasks/1")
        assert found.status_code == 200
        assert found.json() == created.json()

        deleted = client.delete("/tasks/1")
        assert deleted.status_code == 204
        assert client.get("/tasks/1").status_code == 404


def test_invalid_input_and_missing_task() -> None:
    with TestClient(create_app()) as client:
        assert client.post("/tasks", json={"title": ""}).status_code == 422
        assert client.get("/tasks/999").status_code == 404
