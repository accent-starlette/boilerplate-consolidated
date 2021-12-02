from wtforms import fields, form, validators


class LoginForm(form.Form):
    email = fields.EmailField(
        validators=[
            validators.DataRequired(),
            validators.Email(message="Must be a valid email."),
        ]
    )
    password = fields.PasswordField(validators=[validators.DataRequired()])
