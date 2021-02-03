from starlette import status
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse

from app.auth.forms import PasswordChangeForm
from app.utils.templating import templates


class PasswordChange(HTTPEndpoint):
    @requires(["authenticated"])
    async def get(self, request):
        template = "auth/password_change.html"

        form = PasswordChangeForm()
        context = {"request": request, "form": form}
        return templates.TemplateResponse(template, context)

    @requires(["authenticated"])
    async def post(self, request):
        template = "auth/password_change.html"

        data = await request.form()
        form = PasswordChangeForm(data)

        if not form.validate():
            context = {"request": request, "form": form}
            return templates.TemplateResponse(template, context)

        if not request.user.check_password(form.current_password.data):
            form.current_password.errors.append("Enter your current password.")
            context = {"request": request, "form": form}
            return templates.TemplateResponse(template, context)

        else:
            request.user.set_password(form.new_password.data)
            await request.user.save()

        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
