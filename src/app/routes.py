from starlette.routing import Mount, Route

from app import endpoints, static
from app.auth.app import app as auth_app

routes = [
    Route("/", endpoints.Home, methods=["GET"], name="home"),
    Mount("/auth", app=auth_app, name="auth"),
    Mount("/static", app=static.app, name="static"),
]
