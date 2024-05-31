from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired,DataRequired
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired(), DataRequired()])
    password = PasswordField('Password', [InputRequired(), DataRequired()])
    submit = SubmitField('Submit')