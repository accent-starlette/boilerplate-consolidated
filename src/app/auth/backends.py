import sqlalchemy as sa
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    UnauthenticatedUser,
)
from starlette.requests import HTTPConnection

from app.auth.tables import User


class AuthBackend(AuthenticationBackend):
    async def get_user(self, conn: HTTPConnection):
        user_id = conn.session.get("user")
        if user_id:
            try:
                qs = (
                    sa.select(User)
                    .where(User.id == user_id)
                    .options(sa.orm.selectinload(User.scopes))
                )
                result = await User.execute(qs)
                return result.scalars().first()
            except:
                conn.session.pop("user")

    async def authenticate(self, conn: HTTPConnection):
        user = await self.get_user(conn)
        if user and user.is_authenticated:
            scopes = ["authenticated"] + sorted([str(s) for s in user.scopes])
            return AuthCredentials(scopes), user
        scopes = ["unauthenticated"]
        return AuthCredentials(scopes), UnauthenticatedUser()
