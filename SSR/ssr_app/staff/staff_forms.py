from SSR.ssr_app import db
from flask_wtf import FlaskForm
from SSR.ssr_app.models import getLibraries
from wtforms import SubmitField
from wtforms.validators import Optional, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField


class StatForm(FlaskForm):
	library_select = QuerySelectField(query_factory=getLibraries, label='Library', get_label='library_name', allow_blank=True, blank_text="Select a library to see statistics.", validators=[(Optional())])
	lib_submit = SubmitField('Go')
