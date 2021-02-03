from starlette.config import Config
from starlette.datastructures import URL, CommaSeparatedStrings, Secret

from app.utils.database import DatabaseURL

config = Config()

# base
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings)
DATABASE_URL = config("DATABASE_URL", cast=DatabaseURL)
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

# aws
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", cast=Secret, default=None)
AWS_BUCKET = config("AWS_BUCKET", default=None)
AWS_REGION = config("AWS_REGION", default=None)

# env
TESTING = config("TESTING", cast=bool, default=False)
SENTRY_DSN = config("SENTRY_DSN", cast=URL, default=None)

# test
if TESTING:
    DATABASE_URL = DATABASE_URL.replace(database="test_" + DATABASE_URL.database)
