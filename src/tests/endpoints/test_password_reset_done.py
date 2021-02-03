import pytest

from app.main import app


@pytest.mark.asyncio
async def test_get(client):
    url = app.url_path_for("auth:password_reset_done")
    response = await client.get(url)
    assert response.status_code == 200
