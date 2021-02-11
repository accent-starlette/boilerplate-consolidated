from email.message import EmailMessage

import sqlalchemy as sa
from starlette.requests import Request
from wtforms import fields, form, validators
from wtforms.fields.html5 import EmailField

from app.auth.tables import User
from app.auth.tokens import token_generator
from app.utils.base64 import urlsafe_base64_encode
from app.utils.email import send_message
from app.utils.templating import templates


class PasswordResetForm(form.Form):
    email = EmailField(
        validators=[
            validators.DataRequired(),
            validators.Email(message="Must be a valid email."),
        ]
    )

    async def send_email(self, request: Request):
        qs = sa.select(User).where(User.email == self.data["email"])
        result = await User.execute(qs)
        user = result.scalars().first()
        if not user:
            return

        context = {
            "request": request,
            "uid": urlsafe_base64_encode(bytes(str(user.id), encoding="utf-8")),
            "user": user,
            "token": token_generator.make_token(user),
        }
        msg = EmailMessage()

        subject_tmpl = templates.get_template("auth/password_reset_subject.txt")
        subject = subject_tmpl.render(context)
        body_tmpl = templates.get_template("auth/password_reset_body.txt")
        body = body_tmpl.render(context)

        msg["To"] = [user.email]
        msg["Subject"] = subject
        msg.set_content(body)

        await send_message(msg)


class PasswordResetConfirmForm(form.Form):
    new_password = fields.PasswordField(validators=[validators.DataRequired()])
    confirm_new_password = fields.PasswordField(
        validators=[
            validators.DataRequired(),
            validators.EqualTo("new_password", message="The passwords do not match."),
        ]
    )
