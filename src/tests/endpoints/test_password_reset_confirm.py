from datetime import datetime

import pytest

from app.auth.tokens import token_generator
from app.main import app
from app.utils.base64 import urlsafe_base64_encode


@pytest.mark.asyncio
async def test_get_200(client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    response = await client.get(url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invalid_token(client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = "9t9olo-f3de2d54710b829c6a59"
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    response = await client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_invalid_uid(client, user):
    uidb64 = "XX"
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    response = await client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_not_active(client, user):
    user.is_active = False
    await user.save()
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    response = await client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_url_is_invalid_by_logging_in(client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    # here we just update the last_login to simulate the user logging
    # in after the pw request is created
    user.last_login = datetime.utcnow()
    await user.save()

    response = await client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post(client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    response = await client.post(
        url, data={"new_password": "password1", "confirm_new_password": "password1"}
    )
    assert response.status_code == 200
    url = app.url_path_for("auth:password_reset_complete")
    assert response.url == f"http://test{url}"


@pytest.mark.asyncio
async def test_post_changed_password(client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    await client.post(
        url, data={"new_password": "foobar25", "confirm_new_password": "foobar25"}
    )

    await user.refresh_from_db()
    assert user.check_password("foobar25")


@pytest.mark.asyncio
async def test_post_url_is_one_time_use(client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    await client.post(
        url, data={"new_password": "foobar25", "confirm_new_password": "foobar25"}
    )

    another = await client.get(url)
    assert another.status_code == 404


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {"new_password": "", "confirm_new_password": ""},
        {"new_password": " ", "confirm_new_password": " "},
        {"new_password": "password1", "confirm_new_password": "password2"},
    ],
)
@pytest.mark.asyncio
async def test_invalid(test_data, client, user):
    uidb64 = urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8"))
    token = token_generator.make_token(user)
    url = app.url_path_for("auth:password_reset_confirm", uidb64=uidb64, token=token)

    response = await client.post(url, data=test_data)
    assert response.status_code == 200
    assert response.url == f"http://test{url}"
