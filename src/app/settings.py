from sqlalchemy.engine import make_url
from starlette.config import Config
from starlette.datastructures import URL, CommaSeparatedStrings, Secret

config = Config()

# base
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings)
DATABASE_URL = config("DATABASE_URL", cast=make_url)
DEBUG = config("DEBUG", cast=bool, default=False)
SECRET_KEY = config("SECRET_KEY", cast=Secret)

# email
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="app.utils.email.backends.SmtpEmailBackend"
)
EMAIL_DEFAULT_FROM_ADDRESS = config("EMAIL_DEFAULT_FROM_ADDRESS", default="")
EMAIL_DEFAULT_FROM_NAME = config("EMAIL_DEFAULT_FROM_NAME", default="")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=None)
EMAIL_USERNAME = config("EMAIL_USERNAME", default="")
EMAIL_PASSWORD = config("EMAIL_PASSWORD", cast=Secret, default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", cast=int, default=30)

# debugging
TESTING = config("TESTING", cast=bool, default=False)
SENTRY_DSN = config("SENTRY_DSN", cast=URL, default=None)

# test
if TESTING:
    DATABASE_URL = DATABASE_URL.set(database="test_" + DATABASE_URL.database)
