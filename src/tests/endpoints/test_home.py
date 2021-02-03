import pytest

from app.main import app


@pytest.mark.asyncio
async def test_home_get(client):
    url = app.url_path_for("home")
    response = await client.get(url)
    assert response.status_code == 200
