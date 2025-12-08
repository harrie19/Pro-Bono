import json
from datetime import datetime

import pytest
from policy_service import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_policy_approved(client):
    payload = {"command": "read file.txt", "context": {"user_role": "admin"}}
    response = client.post('/policy_check', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["policy_status"] == "approved"


def test_policy_denied(client):
    payload = {"command": "rm -rf /", "context": {"user_role": "admin"}}
    response = client.post('/policy_check', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["policy_status"] == "denied"

