import sqlalchemy as sa
from starlette import status
from starlette.authentication import requires
from starlette.background import BackgroundTask
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse

from app.auth.forms import PasswordResetConfirmForm, PasswordResetForm
from app.auth.tables import User
from app.auth.tokens import token_generator
from app.utils.base64 import urlsafe_base64_decode
from app.utils.templating import templates


class PasswordReset(HTTPEndpoint):
    async def get(self, request):
        template = "auth/password_reset.html"

        form = PasswordResetForm()
        context = {"request": request, "form": form}
        return templates.TemplateResponse(template, context)

    async def post(self, request):
        template = "auth/password_reset.html"

        data = await request.form()
        form = PasswordResetForm(data)

        if not form.validate():
            context = {"request": request, "form": form}
            return templates.TemplateResponse(template, context)

        qs = sa.select(User).where(User.email == form.email.data.lower())
        result = await User.execute(qs)
        user = result.scalars().first()

        background = None
        if user and user.is_active:
            background = BackgroundTask(form.send_email, request=request)

        return RedirectResponse(
            request.url_for("auth:password_reset_done"),
            status_code=status.HTTP_302_FOUND,
            background=background,
        )


class PasswordResetDone(HTTPEndpoint):
    async def get(self, request):
        template = "auth/password_reset_done.html"

        context = {"request": request}
        return templates.TemplateResponse(template, context)


class PasswordResetConfirm(HTTPEndpoint):
    async def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = await User.get(int(uid))
        except:
            user = None
        return user

    def check_token(self, user, uidb64, token) -> bool:
        if not (user and user.is_active):
            return False
        return bool(token_generator.check_token(user, token))

    async def get(self, request):
        template = "auth/password_reset_confirm.html"

        uidb64 = request.path_params["uidb64"]
        token = request.path_params["token"]

        user = await self.get_user(uidb64)

        if not self.check_token(user, uidb64, token):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        form = PasswordResetConfirmForm()
        context = {"request": request, "form": form}
        return templates.TemplateResponse(template, context)

    async def post(self, request):
        template = "auth/password_reset_confirm.html"

        uidb64 = request.path_params["uidb64"]
        token = request.path_params["token"]

        user = await self.get_user(uidb64)

        if not self.check_token(user, uidb64, token):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        data = await request.form()
        form = PasswordResetConfirmForm(data)

        if not form.validate():
            context = {"request": request, "form": form}
            return templates.TemplateResponse(template, context)

        user.set_password(form.new_password.data)
        await user.save()

        return RedirectResponse(
            url=request.url_for("auth:password_reset_complete"),
            status_code=status.HTTP_302_FOUND,
        )


class PasswordResetComplete(HTTPEndpoint):
    async def get(self, request):
        template = "auth/password_reset_complete.html"

        context = {"request": request}
        return templates.TemplateResponse(template, context)
