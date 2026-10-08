import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import ClientBrief
from app.services.brief_extractor import BriefExtractionError

client = TestClient(app)

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
@pytest.fixture
def valid_request_payload():
    """A minimal valid request body for the extract endpoint."""
    return {"message": "We need a mobile app for our bakery with a budget of $5000."}

@pytest.fixture
def mock_extracted_brief():
    """A sample ClientBrief object returned by the mocked extractor."""
    return ClientBrief(
        client_name="Sweet Treats Bakery",
        business_type="Food & Beverage",
        project_type="Mobile App",
        requested_features=["online ordering", "loyalty program"],
        budget=5000.0,
        currency="USD",
        deadline=None,
        missing_information=[],
        extraction_confidence="high",
    )

# ------------------------------------------------------------------
# Successful extraction
# ------------------------------------------------------------------
@patch("app.main.extract_client_brief", new_callable=AsyncMock)
def test_extract_brief_success(mock_extract, valid_request_payload, mock_extracted_brief):
    """When the service succeeds, the endpoint returns the parsed ClientBrief."""
    mock_extract.return_value = mock_extracted_brief

    response = client.post("/briefs/extract", json=valid_request_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["client_name"] == "Sweet Treats Bakery"
    assert data["budget"] == 5000.0
    assert data["extraction_confidence"] == "high"
    mock_extract.assert_awaited_once_with(valid_request_payload["message"])

# ------------------------------------------------------------------
# Validation errors (Pydantic)
# ------------------------------------------------------------------
def test_extract_brief_message_too_short():
    """Messages under 10 characters should return a 422 validation error."""
    response = client.post("/briefs/extract", json={"message": "Hi"})
    assert response.status_code == 422
    assert "min_length" in str(response.json())

def test_extract_brief_message_missing():
    """Missing the required 'message' field should return a 422."""
    response = client.post("/briefs/extract", json={})
    assert response.status_code == 422

def test_extract_brief_message_too_long():
    """Messages over 10,000 characters should return a 422."""
    long_message = "a" * 10_001
    response = client.post("/briefs/extract", json={"message": long_message})
    assert response.status_code == 422

# ------------------------------------------------------------------
# Service failure
# ------------------------------------------------------------------
@patch("app.main.extract_client_brief", new_callable=AsyncMock)
def test_extract_brief_service_error(mock_extract, valid_request_payload):
    """When the service raises BriefExtractionError, the endpoint returns 502."""
    mock_extract.side_effect = BriefExtractionError("Model failed")

    response = client.post("/briefs/extract", json=valid_request_payload)

    assert response.status_code == 502
    assert response.json()["detail"] == "The client brief could not be extracted."
    mock_extract.assert_awaited_once()