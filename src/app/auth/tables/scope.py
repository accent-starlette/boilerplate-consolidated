import sqlalchemy as sa

from app.utils.database import ModelBase


class Scope(ModelBase):
    code = sa.Column(sa.String(50), nullable=False, unique=True)
    description = sa.Column(sa.Text)

    def __str__(self):
        return self.code
