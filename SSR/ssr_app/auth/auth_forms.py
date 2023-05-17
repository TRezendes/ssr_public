"""
Copyright (c) 2022–2023 Timothy Rezendes

This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Simple Summer Reading is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from ssr_app import db
from flask_wtf import FlaskForm
from ssr_app.models import LibraryTbl, LoginInfoTbl, StaffTbl, UserInfoTbl
from wtforms import BooleanField, EmailField, HiddenField, PasswordField, StringField, SubmitField, TelField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, ValidationError
from wtforms_validators import AlphaNumeric
from wtforms_sqlalchemy.fields import QuerySelectField
from uuid import uuid4


# Registration and Login based on example code from:
# https://github.com/jimdevops19/codesnippets/tree/main/Flask%20Full%20Series
class RegistrationForm(FlaskForm):
	# Custom field validators check ensure duplicate the username and email addresses being registereed are unique in the system
	def validate_username(self, username_to_check):
		username = LoginInfoTbl.query.filter_by(username=username_to_check.data).first()
		if username:
			raise ValidationError('An account with this username already exists. Please try a different username.')

	def validate_email_address(self, email_address_to_check):
			email_address = UserInfoTbl.query.filter_by(email_address_user=email_address_to_check.data).first()
			if email_address:
				raise ValidationError('An account with this email address already exists. Please try a different email address.')
	username = StringField(
		label='Choose a Username',
		validators=[Length(min=4, max=42, message='Please choose a username that is between 4 & 42 characters long.'), AlphaNumeric(), InputRequired()]
	)
	full_name = StringField(label='Full Name', validators=[InputRequired()])
	email_address = EmailField(label='E-Mail Address', validators=[Email(), InputRequired()])
	phone_number = TelField(label='Phone Number', validators=[Length(min=10, max=18)])
	password1 = PasswordField(
		label='Password:',
		validators=[Length(min=8, max=232, message='Please choose a password that is between 8 & 232 characters long.'), InputRequired()]
	)
	password2 = PasswordField(
		label='Confirm Password:',
		validators=[EqualTo('password1', message='"Confirm Password" did not match "Password". Please Try Again'), InputRequired()]
	)
	staff_id = PasswordField(label='Employee ID')
	staff_bool = BooleanField(label='Staff Account')
	submit = SubmitField(label='Create Account')

class StaffRegForm(FlaskForm):
	employer = QuerySelectField(label='Employer', validators=[DataRequired()], get_label='library_name', allow_blank=True, blank_text='Please select your employer from the list…')
	job_title = StringField(label='What is your position?')

class LoginForm(FlaskForm):
	username = StringField(label='Username', validators=[InputRequired()])
	password = PasswordField(label='Password', validators=[InputRequired()])
	submit = SubmitField(label='Sign In')

class FileForm(FlaskForm):
	file = FileField('Upload a .csv file of Employee IDs and roles.', validators=[FileRequired()])
	submit = SubmitField('Import Employee File')
