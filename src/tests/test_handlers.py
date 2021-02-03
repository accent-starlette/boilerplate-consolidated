from copy import copy

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_404(client):
    response = await client.get("/invalid-url")
    assert response.status_code == 404
    assert "404" in str(response.content)


@pytest.mark.asyncio
async def test_500():
    async def force_error(request):
        raise RuntimeError()

    copy_app = copy(app)
    copy_app.debug = False
    copy_app.add_route("/force-error", force_error)

    transport = ASGITransport(
        app=copy_app,
        client=("1.2.3.4", 123),
        raise_app_exceptions=False,
    )

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/force-error")
        assert response.status_code == 500
        assert "500" in str(response.content)
