import pytest

from app.main import app


@pytest.mark.asyncio
async def test_get(client, user):
    url = app.url_path_for("auth:login")
    await client.post(url, data={"email": user.email, "password": "pass"})

    url = app.url_path_for("auth:password_change")
    response = await client.get(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_requires_login(client):
    url = app.url_path_for("auth:password_change")
    response = await client.get(url)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_can_change_password(client, user, login):
    url = app.url_path_for("auth:password_change")
    response = await client.post(
        url,
        data={
            "current_password": "pass",
            "new_password": "p@ss",
            "confirm_new_password": "p@ss",
        },
    )
    assert response.status_code == 302
    assert response.is_redirect
    assert response.next_request.url == "http://test/"

    # can then use new password
    url = app.url_path_for("auth:logout")
    response = await client.get(url)
    assert response.status_code == 302
    assert response.is_redirect
    assert response.next_request.url == "http://test/"

    url = app.url_path_for("auth:login")
    response = await client.post(url, data={"email": user.email, "password": "p@ss"})
    assert response.status_code == 302
    assert response.is_redirect
    assert response.next_request.url == "http://test/"


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {
            "current_password": "",
            "new_password": "",
            "confirm_new_password": "",
        },
        {
            "current_password": " ",
            "new_password": " ",
            "confirm_new_password": " ",
        },
        {
            "current_password": "password",
            "new_password": "password1",
            "confirm_new_password": "password2",
        },
        {
            "current_password": "password1",
            "new_password": "password",
            "confirm_new_password": "password",
        },
    ],
)
@pytest.mark.asyncio
async def test_invalid(test_data, client, user, login):
    url = app.url_path_for("auth:password_change")
    response = await client.post(url, data=test_data)
    assert response.status_code == 200
    assert response.url == f"http://test{url}"
