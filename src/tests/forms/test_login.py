import pytest

from app.auth.forms import LoginForm
from app.utils.testing import DummyPostData


def test_valid():
    data = {"email": "stu@example.com", "password": "password"}
    form = LoginForm(DummyPostData(data))
    assert form.validate()
    assert form.data == data


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {"email": "", "password": ""},
        {"email": " ", "password": " "},
        {"email": "invalid", "password": ""},
        {"email": "invalid.com", "password": ""},
        {"email": "invalid@invalid", "password": ""},
    ],
)
def test_invalid(test_data):
    form = LoginForm(DummyPostData(test_data))
    assert form.validate() is False
    assert "email" in form.errors
    assert "password" in form.errors
