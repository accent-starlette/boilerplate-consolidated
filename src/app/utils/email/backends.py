import sys
import typing
from email.message import EmailMessage

import aiosmtplib

from app import settings


class BaseEmailBackend:
    """
    Base class for email backend implementations.
    Subclasses must at least overwrite send_messages().
    open() and close() can be called indirectly by using a backend object as a
    context manager:
       with backend as connection:
           # do something with connection
           pass
    """

    def __init__(self, fail_silently: bool = False, **kwargs: typing.Any) -> None:
        self.fail_silently = fail_silently

    async def open(self):
        """
        Open a network connection.
        This method can be overwritten by backend implementations to open a network
        connection.
        It's up to the backend implementation to track the status of a network
        connection if it's needed by the backend.
        This method can be called by applications to force a single network connection
        to be used when sending mails. See the send_messages() method of the SMTP
        backend for a reference implementation.
        The default implementation does nothing.
        """

    async def close(self):
        """Close a network connection."""

    async def __enter__(self):
        try:
            await self.open()
        except Exception:
            await self.close()
            raise
        return self

    async def __exit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def send_messages(self, email_messages: typing.List[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """

        msg = "subclasses of BaseEmailBackend must override send_messages() method"
        raise NotImplementedError(msg)


class ConsoleEmailBackend(BaseEmailBackend):
    """ A wrapper that sends email to the console. """

    def __init__(self, fail_silently: bool = False, **kwargs: typing.Any) -> None:
        super().__init__(fail_silently=fail_silently)
        self.stream = kwargs.pop("stream", sys.stdout)

    async def write_message(self, message):
        msg_data = message.as_bytes()
        charset = (
            message.get_charset().get_output_charset()
            if message.get_charset()
            else "utf-8"
        )
        msg_data = msg_data.decode(charset)
        self.stream.write("%s\n" % msg_data)
        self.stream.write("-" * 79)
        self.stream.write("\n")

    async def send_messages(self, email_messages: typing.List[EmailMessage]) -> int:
        """ Write all messages to the stream in a thread-safe way. """

        if not email_messages:
            return 0
        msg_count = 0
        try:
            stream_created = await self.open()
            for message in email_messages:
                await self.write_message(message)
                self.stream.flush()
                msg_count += 1
            if stream_created:
                await self.close()
        except Exception:
            if not self.fail_silently:
                raise
        return msg_count


class SmtpEmailBackend(BaseEmailBackend):
    """ A wrapper that manages the SMTP network connection. """

    host = settings.EMAIL_HOST
    port = settings.EMAIL_PORT
    username = settings.EMAIL_USERNAME
    password = settings.EMAIL_PASSWORD
    use_tls = settings.EMAIL_USE_TLS
    timeout = settings.EMAIL_TIMEOUT
    connection = None

    async def open(self):
        """
        Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.
        """

        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        connection_params = {}
        if self.timeout is not None:
            connection_params["timeout"] = self.timeout

        try:
            self.connection = aiosmtplib.SMTP(
                hostname=self.host, port=self.port, **connection_params
            )

            await self.connection.connect()

            if self.use_tls:
                await self.connection.starttls()

            if self.username and self.password:
                await self.connection.login(self.username, str(self.password))

            return True
        except OSError:
            if not self.fail_silently:
                raise

    async def close(self):
        """Close the connection to the email server."""

        if self.connection is None:
            return

        try:
            try:
                await self.connection.quit()
            except:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    async def send_messages(self, email_messages: typing.List[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """

        if not email_messages:
            return 0

        new_conn_created = await self.open()
        if not self.connection or new_conn_created is None:
            # We failed silently on open(). Trying to send would be pointless.
            return 0
        num_sent = 0
        for message in email_messages:
            sent = await self._send(message)
            if sent:
                num_sent += 1
        if new_conn_created:
            await self.close()

        return num_sent

    async def _send(self, email_message: EmailMessage):
        """A helper method that does the actual sending."""

        if not self.connection:
            # We failed silently on open(). Trying to send would be pointless.
            return False

        try:
            await self.connection.send_message(email_message)
        except:
            if not self.fail_silently:
                raise
            return False

        return True
