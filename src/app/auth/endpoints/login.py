from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm.exc import NoResultFound
from starlette import status
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse

from app.auth.forms import LoginForm
from app.auth.tables import User
from app.utils.templating import templates


class Login(HTTPEndpoint):
    async def get(self, request):
        template = "/auth/login.html"

        form = LoginForm()
        context = {"request": request, "form": form}
        return templates.TemplateResponse(template, context)

    async def post(self, request):
        template = "/auth/login.html"

        data = await request.form()
        form = LoginForm(data)

        if not form.validate():
            context = {"request": request, "form": form}
            return templates.TemplateResponse(template, context)

        try:
            qs = sa.select(User).where(User.email == form.email.data.lower())
            result = await User.execute(qs)
            user = result.scalars().one()
            if user.check_password(form.password.data):
                request.session["user"] = str(user.id)
                user.last_login = datetime.utcnow()
                await user.save()
                return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

        except NoResultFound:
            pass

        request.session.clear()

        form.password.errors.append("Invalid email or password.")
        context = {"request": request, "form": form}

        return templates.TemplateResponse(template, context)
