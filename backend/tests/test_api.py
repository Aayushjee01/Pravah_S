"""Tests for the prediction API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /api/v1/health endpoint."""

    def test_health_check_returns_200(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "model_loaded" in data
        assert "environment" in data

    def test_health_check_status_healthy(self):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_app_info(self):
        response = client.get("/")
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestPredictionEndpoint:
    """Tests for the /api/v1/predict endpoint."""

    VALID_PAYLOAD = {
        "location": "Kharghar",
        "area_sqft": 1000.0,
        "bhk": 2,
        "bathrooms": 2,
        "floor": 5,
        "total_floors": 20,
        "age_of_property": 5.0,
        "parking": True,
        "lift": True,
    }

    def test_predict_with_valid_input(self):
        """Test prediction with valid inputs (requires model to be loaded)."""
        response = client.post("/api/v1/predict", json=self.VALID_PAYLOAD)
        # May return 503 if model not loaded in test environment
        assert response.status_code in (200, 503)

    def test_predict_with_invalid_area_too_small(self):
        """Test that area below 100 sqft is rejected."""
        payload = {**self.VALID_PAYLOAD, "area_sqft": 50.0}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_with_invalid_bhk(self):
        """Test that BHK > 6 is rejected."""
        payload = {**self.VALID_PAYLOAD, "bhk": 10}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_with_missing_required_field(self):
        """Test that missing required fields are rejected."""
        payload = {"location": "Kharghar", "area_sqft": 1000.0}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_with_negative_floor(self):
        """Test that negative floor is rejected."""
        payload = {**self.VALID_PAYLOAD, "floor": -1}
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422


class TestLocationsEndpoint:
    """Tests for the /api/v1/locations endpoint."""

    def test_locations_returns_response(self):
        response = client.get("/api/v1/locations")
        assert response.status_code in (200, 503)


class TestModelInfoEndpoint:
    """Tests for the /api/v1/model-info endpoint."""

    def test_model_info_returns_response(self):
        response = client.get("/api/v1/model-info")
        assert response.status_code in (200, 503)
