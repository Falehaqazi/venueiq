import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

os.environ["GOOGLE_API_KEY"] = "test-key-for-testing"

with patch("google.generativeai.configure"), patch("google.generativeai.GenerativeModel"):
    from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VenueIQ"


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "VenueIQ" in response.text


def test_analyze_missing_report():
    response = client.post("/analyze", json={"mode": "crowd"})
    assert response.status_code == 400
    assert "required" in response.json()["detail"].lower()


def test_analyze_report_too_short():
    response = client.post("/analyze", json={"report": "short", "mode": "crowd"})
    assert response.status_code == 400


def test_analyze_invalid_mode():
    response = client.post("/analyze", json={"report": "A" * 50, "mode": "invalid_mode"})
    assert response.status_code == 400
    assert "Invalid mode" in response.json()["detail"]


def test_analyze_report_too_long():
    response = client.post("/analyze", json={"report": "A" * 6000, "mode": "crowd"})
    assert response.status_code == 400


def test_analyze_valid_modes():
    valid_modes = ["crowd", "wait", "coord"]
    mock_response = MagicMock()
    mock_response.text = "Mock AI analysis response for testing"
    with patch("main.model.generate_content", return_value=mock_response):
        for mode in valid_modes:
            response = client.post("/analyze", json={
                "report": "Gate C showing heavy congestion with 3000 fans backing up toward concourse.",
                "mode": mode
            })
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            assert response.json()["mode"] == mode


def test_analyze_invalid_json():
    response = client.post("/analyze", content="not json", headers={"Content-Type": "application/json"})
    assert response.status_code == 400


def test_analyze_success_response_structure():
    mock_response = MagicMock()
    mock_response.text = "1. CROWD STATUS: Heavy congestion at Gate C."
    with patch("main.model.generate_content", return_value=mock_response):
        response = client.post("/analyze", json={
            "report": "Gate C showing heavy congestion with 3000 fans backing up toward the main concourse area.",
            "mode": "crowd"
        })
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "mode" in data
        assert "status" in data
