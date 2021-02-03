import pytest

from app.auth.forms import PasswordResetForm
from app.utils.testing import DummyPostData


def test_valid():
    data = {"email": "stu@example.com"}
    form = PasswordResetForm(DummyPostData(data))
    assert form.validate()
    assert form.data == data


@pytest.mark.parametrize(
    "test_data",
    [
        {},
        {"email": ""},
        {"email": " "},
        {"email": "invalid"},
        {"email": "invalid.com"},
        {"email": "invalid@invalid"},
    ],
)
def test_invalid(test_data):
    form = PasswordResetForm(DummyPostData(test_data))
    assert form.validate() is False
    assert "email" in form.errors
