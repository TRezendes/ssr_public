"""
Copyright (c) 2022 Timothy Rezendes

This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Foobar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from SSR.ssr_app import db
from flask_wtf import FlaskForm
from SSR.ssr_app.models import getLibraries
from wtforms import SubmitField
from wtforms.validators import Optional, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField


class StatForm(FlaskForm):
	library_select = QuerySelectField(query_factory=getLibraries, label='Library', get_label='library_name', allow_blank=True, blank_text="Select a library to see statistics.", validators=[(Optional())])
	lib_submit = SubmitField('Go')
