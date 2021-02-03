import pytest

from app.auth.forms import PasswordResetConfirmForm
from app.utils.testing import DummyPostData


def test_valid():
    data = {"new_password": "password", "confirm_new_password": "password"}
    form = PasswordResetConfirmForm(DummyPostData(data))
    assert form.validate()
    assert form.data == data


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {"new_password": "", "confirm_new_password": ""},
        {"new_password": " ", "confirm_new_password": " "},
    ],
)
def test_invalid(test_data):
    form = PasswordResetConfirmForm(DummyPostData(test_data))
    assert form.validate() is False
    assert "new_password" in form.errors
    assert "confirm_new_password" in form.errors


def test_passwords_dont_match():
    data = {"new_password": "password1", "confirm_new_password": "password2"}
    form = PasswordResetConfirmForm(DummyPostData(data))
    assert form.validate() is False
    assert form.errors == {"confirm_new_password": ["The passwords do not match."]}
