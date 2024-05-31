from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired


class RegisterForm(FlaskForm):
    username = StringField("Username", [InputRequired(), DataRequired()])
    password = PasswordField("Password", [InputRequired(), DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", [InputRequired(), DataRequired()])
    password = PasswordField("Password", [InputRequired(), DataRequired()])
    submit = SubmitField("Submit")
