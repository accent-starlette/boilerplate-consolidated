from datetime import datetime, timedelta

import pytest

from app.auth.tables import User
from app.auth.tokens import RESET_PW_TIMEOUT_SECONDS, PasswordResetTokenGenerator


def test_make_token(user):
    p0 = PasswordResetTokenGenerator()
    tk1 = p0.make_token(user)
    assert p0.check_token(user, tk1)


@pytest.mark.asyncio
async def test_django_bug_10265(user):
    p0 = PasswordResetTokenGenerator()
    tk1 = p0.make_token(user)
    reload = await User.get(user.id)
    tk2 = p0.make_token(reload)
    assert tk1 == tk2


def test_timeout(user):
    """The token is valid after n seconds, but no greater."""
    # Uses a mocked version of PasswordResetTokenGenerator so we can change
    # the value of 'now'.

    class Mocked(PasswordResetTokenGenerator):
        def __init__(self, now):
            self._now_val = now

        def _now(self):
            return self._now_val

    p0 = PasswordResetTokenGenerator()
    tk1 = p0.make_token(user)

    p1 = Mocked(datetime.utcnow() + timedelta(seconds=RESET_PW_TIMEOUT_SECONDS))
    assert p1.check_token(user, tk1)

    p2 = Mocked(datetime.utcnow() + timedelta(seconds=(RESET_PW_TIMEOUT_SECONDS + 1)))
    assert not p2.check_token(user, tk1)

    p3 = Mocked(datetime.utcnow() + timedelta(seconds=RESET_PW_TIMEOUT_SECONDS))
    assert p3.check_token(user, tk1)
    p4 = Mocked(datetime.utcnow() + timedelta(seconds=(RESET_PW_TIMEOUT_SECONDS + 1)))
    assert not p4.check_token(user, tk1)


def test_check_token_with_nonexistent_token_and_user(user):
    p0 = PasswordResetTokenGenerator()
    tk1 = p0.make_token(user)
    assert not p0.check_token(None, tk1)
    assert not p0.check_token(user, None)
