import json
import pytest
from pathlib import Path
import os
from flight_recorder_service import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    log_path = tmp_path / "flight_recorder.log"
    monkeypatch.setenv("FLIGHT_RECORDER_LOG", str(log_path))
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"

def test_record_event(client, tmp_path):
    payload = {
        "command": "Zeit",
        "policy_status": "approved",
        "result": "Aktuelle Zeit: ...",
        "metadata": {"source": "test"},
    }

    response = client.post('/flight_record', json=payload)
    assert response.status_code == 200
    assert response.get_json()["status"] == "recorded"

    log_path = tmp_path / "flight_recorder.log"
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["command"] == "Zeit"
