from starlette import status
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse


class Logout(HTTPEndpoint):
    async def get(self, request):
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
