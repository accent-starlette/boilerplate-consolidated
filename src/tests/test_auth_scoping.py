from copy import copy

import pytest
from httpx import AsyncClient
from starlette.authentication import requires
from starlette.responses import JSONResponse

from app.auth.tables import Scope
from app.main import app


@requires(["unauthenticated"])
def unauthed(request):
    return JSONResponse({"status": "ok"})


@requires(["authenticated"])
def authed(request):
    return JSONResponse({"status": "ok"})


@requires(["authenticated", "read"])
def read(request):
    return JSONResponse({"status": "ok"})


@requires(["authenticated", "write"])
def write(request):
    return JSONResponse({"status": "ok"})


@pytest.mark.asyncio
async def test_scoped_endpoints(user):
    read_scope = Scope(code="read")
    write_scope = Scope(code="write")

    await read_scope.save()
    await write_scope.save()

    copy_app = copy(app)

    copy_app.add_route("/unauthed", unauthed)
    copy_app.add_route("/authed", authed)
    copy_app.add_route("/read", read)
    copy_app.add_route("/write", write)

    async with AsyncClient(app=copy_app, base_url="http://test") as client:
        assert (await client.get("/unauthed")).status_code == 200
        assert (await client.get("/authed")).status_code == 403
        assert (await client.get("/read")).status_code == 403
        assert (await client.get("/write")).status_code == 403

        url = copy_app.url_path_for("auth:login")
        login = await client.post(url, data={"email": user.email, "password": "pass"})

        assert login.status_code == 302
        assert login.is_redirect
        assert login.next_request.url == "http://test/"

        assert (await client.get("/unauthed")).status_code == 403
        assert (await client.get("/authed")).status_code == 200
        assert (await client.get("/read")).status_code == 403
        assert (await client.get("/write")).status_code == 403

        user.scopes.append(read_scope)
        await user.save()

        assert (await client.get("/unauthed")).status_code == 403
        assert (await client.get("/authed")).status_code == 200
        assert (await client.get("/read")).status_code == 200
        assert (await client.get("/write")).status_code == 403

        user.scopes.append(write_scope)
        await user.save()

        assert (await client.get("/unauthed")).status_code == 403
        assert (await client.get("/authed")).status_code == 200
        assert (await client.get("/read")).status_code == 200
        assert (await client.get("/write")).status_code == 200
