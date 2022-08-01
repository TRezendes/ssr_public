"""
This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Foobar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from flask_wtf import FlaskForm
from SSR.ssr_app.models import LibraryTbl, LoginInfoTbl, StaffTbl, UserInfoTbl, ZipTbl, getSchools, getStates
from wtforms import BooleanField, DateField, DecimalField, EmailField, FloatField, FormField, HiddenField, IntegerField, RadioField, SelectField, StringField, SubmitField, TelField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional, ValidationError
from wtforms_validators import AlphaNumeric
from wtforms_sqlalchemy.fields import QuerySelectField
from uuid import uuid4
import datetime


class ReaderRegForm(FlaskForm):
	# Custom validator adapted from https://stackoverflow.com/questions/61533996/flask-wtform-datefield-to-only-accept-today-and-future-dates-only,
	# answer by RianneJ: https://stackoverflow.com/users/11376173/riannej
	def validate_dob(form, field):
		if field.data > datetime.date.today():
			raise ValidationError("Please do not enter future dates.")

	name = StringField("Reader's Name", validators=[InputRequired()])
	school_bool = RadioField('Does the Reader Attend School?', choices=['No', 'Yes'], coerce=str)
	school0 = HiddenField()
	school1 = QuerySelectField(query_factory=getSchools, label='School', get_label='school_name', allow_blank=True, blank_text="Please select the reader's school from the list…", validators=[(Optional())])	
	dob = DateField("Reader's Date of Birth", validators=[InputRequired()])
	mailing_address = StringField('Mailing Address', validators=[Length(max=50), InputRequired()])
	city = StringField('City', validators=[Length(max=35), InputRequired()])
	state = QuerySelectField(query_factory=getStates, label='State', get_label='state_name', allow_blank=False, validators=[InputRequired()])
	zip5 = StringField('ZIP Code', validators=[Length(min=5, max=5), InputRequired()])
	zip4 = StringField('ZIP+4', validators=[Optional(), Length(min=4, max=4)])
	submit = SubmitField(label='Create Reader')
	
class ProgressForm(FlaskForm):
	activity_check1 = BooleanField(validators=[Optional()])
	activity_check2 = BooleanField(validators=[Optional()])
	activity_check3 = BooleanField(validators=[Optional()])
	activity_check4 = BooleanField(validators=[Optional()])
	activity_check5 = BooleanField(validators=[Optional()])
	activity_check6 = BooleanField(validators=[Optional()])
	activity_check7 = BooleanField(validators=[Optional()])
	activity_check8 = BooleanField(validators=[Optional()])
	activity_check9 = BooleanField(validators=[Optional()])
	activity_check10 = BooleanField(validators=[Optional()])
	activity_check11 = BooleanField(validators=[Optional()])
	activity_check12 = BooleanField(validators=[Optional()])
	time_entry = FloatField(validators=[Optional(), NumberRange(min=0, max=99, message="Time entered must not be negative, and if you've read more than 99 hours, congratulations, but you can't enter it all at once." )])
	time_unit = SelectField('Time Unit', validators=[Optional()], choices=['Minutes', 'Hours'])
	books_entry = IntegerField('Add to Total Books Read', validators=[Optional(), NumberRange(min=0, max=999, message="Books entered must not be negative, and if you've read more than 999 books, congratulations, but you can't enter them all at once." )])
	answer_1 = TextAreaField('Answer Question 1', validators=[Optional(), Length(min=3, max=1000)])
	answer_2 = TextAreaField('Answer Question 2', validators=[Optional(), Length(min=3, max=1000)])
	answer_3 = TextAreaField('Answer Question 3', validators=[Optional(), Length(min=3, max=1000)])
	submit = SubmitField('Update Completed Goals')

class DeleteReaderForm (FlaskForm):
	delete = SubmitField('Delete Reader')