import pytest

from app.main import app


@pytest.mark.asyncio
async def test_get(client):
    url = app.url_path_for("auth:login")
    response = await client.get(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_can_login(client, user):
    url = app.url_path_for("auth:login")
    response = await client.post(url, data={"email": user.email, "password": "pass"})
    assert response.status_code == 200
    assert response.url == "http://test/"
    assert "session" in response.cookies


@pytest.mark.asyncio
async def test_user_last_login_set(client, user):
    assert user.last_login is None
    url = app.url_path_for("auth:login")
    await client.post(url, data={"email": user.email, "password": "pass"})
    await user.refresh_from_db()
    assert user.last_login is not None


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {"email": "", "password": ""},
        {"email": " ", "password": " "},
        {"email": "user@example.com", "password": "password1"},
        {"email": "bob@example.com", "password": "password"},
    ],
)
@pytest.mark.asyncio
async def test_invalid_credentials(test_data, client, user):
    url = app.url_path_for("auth:login")
    response = await client.post(url, data=test_data)
    assert response.status_code == 200
    assert response.url == f"http://test{url}"
