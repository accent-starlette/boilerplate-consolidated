import pytest

from app.main import app


@pytest.mark.asyncio
async def test_get(client):
    url = app.url_path_for("auth:password_reset")
    response = await client.get(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_redirects(client, monkeypatch):
    # its important here that the post will redirect regardless
    # of whether the user exists or not so we specifally dont use a valid email

    async def fake_send(msg):
        raise Exception("An email should not have been sent")

    monkeypatch.setattr("app.auth.forms.password_reset.send_message", fake_send)

    url = app.url_path_for("auth:password_reset")
    response = await client.post(url, data={"email": "fake@example.com"})
    assert response.status_code == 200
    url = app.url_path_for("auth:password_reset_done")
    assert response.url == f"http://test{url}"


@pytest.mark.asyncio
async def test_email_not_sent_if_user_is_not_active(client, user, monkeypatch):
    user.is_active = False
    await user.save()

    async def fake_send(msg):
        raise Exception("An email should not have been sent")

    monkeypatch.setattr("app.auth.forms.password_reset.send_message", fake_send)

    url = app.url_path_for("auth:password_reset")
    response = await client.post(url, data={"email": user.email})
    assert response.status_code == 200
    url = app.url_path_for("auth:password_reset_done")
    assert response.url == f"http://test{url}"


@pytest.mark.asyncio
async def test_txt_email_sent_if_user_exists(client, user, monkeypatch):
    async def fake_send(msg):
        assert msg.get_content_maintype() == "text"
        assert msg["To"] == user.email

    monkeypatch.setattr("app.auth.forms.password_reset.send_message", fake_send)

    url = app.url_path_for("auth:password_reset")
    response = await client.post(url, data={"email": user.email})
    assert response.status_code == 200
    url = app.url_path_for("auth:password_reset_done")
    assert response.url == f"http://test{url}"


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {"email": ""},
        {"email": " "},
        {"email": "invalid"},
        {"email": "user@invalid"},
    ],
)
@pytest.mark.asyncio
async def test_invalid_data(test_data, client, user):
    url = app.url_path_for("auth:password_reset")
    response = await client.post(url, data=test_data)

    assert response.status_code == 200
    assert response.url == f"http://test{url}"
