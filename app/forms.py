from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired

from config import Config
from buffer import Buffer
from oj import OJ

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')

class SubmitForm(FlaskForm):
	problem = SelectField('Problem', choices=[(str(pid), Buffer.problems[pid]["title"]) for pid in Config.data["Problems"]], validators=[DataRequired()])
        language = SelectField('Language', choices=sorted([(str(lid), lang) for lang, lid in OJ.Languages.items()], key=lambda x : -100 if int(x[0])==2 else int(x[0])), validators=[DataRequired()])
	code = FileField(validators=[DataRequired()])
	submit = SubmitField('Submit')
