import sqlalchemy as sa

from app.auth.tables import Scope
from app.utils.testing import assert_model_field

data = {"code": "read", "description": "read access"}


def test_fields():
    assert_model_field(Scope, "code", sa.String, False, False, True, 50)
    assert_model_field(Scope, "description", sa.Text, True, False, False)


def test_model_data():
    scope = Scope(**data)

    assert scope.code == "read"
    assert scope.description == "read access"


def test_str():
    scope = Scope(**data)

    assert str(scope) == "read"
