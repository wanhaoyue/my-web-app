import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sentiment" in response.data


def test_positive_sentiment(client):
    response = client.post(
        "/api/sentiment",
        json={"text": "I love this product, it is great and wonderful!"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["sentiment"] == "Positive"
    assert data["polarity"] > 0.1


def test_negative_sentiment(client):
    response = client.post(
        "/api/sentiment",
        json={"text": "This is terrible and awful, I hate it."},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["sentiment"] == "Negative"
    assert data["polarity"] < -0.1


def test_missing_text_field_returns_400(client):
    response = client.post("/api/sentiment", json={"message": "hello"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_empty_text_returns_400(client):
    response = client.post("/api/sentiment", json={"text": "   "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Text cannot be empty"