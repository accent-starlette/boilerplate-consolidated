from starlette.routing import Router

from app.auth.routes import routes

app = Router(routes)
