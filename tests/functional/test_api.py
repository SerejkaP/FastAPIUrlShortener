import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_short_link():
    response = client.post(
        "/links/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    assert "links/" in response.text


@pytest.mark.asyncio
async def test_get_short_link_stats():
    response = client.get("/links/test_code/stats")
    assert response.status_code == 404  # Нет такой ссылки


@pytest.mark.asyncio
async def test_redirect_short_link():
    response = client.get("/links/test_code", allow_redirects=False)
    assert response.status_code == 404
