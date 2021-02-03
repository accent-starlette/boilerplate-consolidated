from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app import settings
from app.auth.backends import AuthBackend

middleware = [
    Middleware(CORSMiddleware, allow_origins=settings.ALLOWED_HOSTS),
    Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
    Middleware(AuthenticationMiddleware, backend=AuthBackend()),
]
