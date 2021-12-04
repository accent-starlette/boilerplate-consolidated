import pytest

from app.main import app


@pytest.mark.asyncio
async def test_login_get(user, client, login):
    url = app.url_path_for("auth:logout")
    response = await client.get(url)
    assert response.status_code == 302
    assert response.is_redirect
    assert response.next_request.url == "http://test/"
    assert "session" not in response.cookies
