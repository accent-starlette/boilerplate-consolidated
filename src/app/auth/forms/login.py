from wtforms import fields, form, validators
from wtforms.fields.html5 import EmailField


class LoginForm(form.Form):
    email = EmailField(
        validators=[
            validators.DataRequired(),
            validators.Email(message="Must be a valid email."),
        ]
    )
    password = fields.PasswordField(validators=[validators.DataRequired()])
