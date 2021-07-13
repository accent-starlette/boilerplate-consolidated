import email.utils
import typing
from email.message import EmailMessage

from app import settings
from app.utils.email.backends import BaseEmailBackend
from app.utils.klass import import_string


def get_connection(
    backend: typing.Optional[str] = None,
    fail_silently: bool = False,
    **kwds: typing.Any
):
    """Load an email backend and return an instance of it.
    If backend is None (default), use config.email_backend.
    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    klass = import_string(backend or settings.EMAIL_BACKEND)
    return klass(fail_silently=fail_silently, **kwds)


async def send_message(
    msg: EmailMessage,
    connection: typing.Optional[BaseEmailBackend] = None,
    fail_silently: bool = False,
):
    """Send an ``email.message.EmailMessage``."""

    if not msg.get("From"):
        msg["From"] = email.utils.formataddr(
            (settings.EMAIL_DEFAULT_FROM_NAME, settings.EMAIL_DEFAULT_FROM_ADDRESS)
        )

    connection = connection or get_connection(fail_silently=fail_silently)
    return await connection.send_messages([msg])
