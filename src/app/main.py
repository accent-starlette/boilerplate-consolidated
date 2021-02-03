from starlette.applications import Starlette

from app import db, exceptions, middleware, routes, settings

app = Starlette(
    debug=settings.DEBUG,
    routes=routes.routes,
    middleware=middleware.middleware,
    exception_handlers=exceptions.error_handlers,  # type: ignore
)

if settings.SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        sentry_sdk.init(str(settings.SENTRY_DSN))
        app.add_middleware(SentryAsgiMiddleware)
    except ImportError:
        pass
