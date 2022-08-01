"""
Copyright (c) 2022 Timothy Rezendes

This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Foobar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from SSR.ssr_app import argon2, db
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects import postgresql
from sqlalchemy import PrimaryKeyConstraint

# All model classes take advantage of SQLAlchemy's ability to "reflect" existing relations
# https://docs.sqlalchemy.org/en/14/core/reflection.html
class ActivityTbl(db.Model):
	__tablename__ = 'activity'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class CompActsTbl(db.Model):
	__tablename__ = 'completed_activities'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class GoalTbl(db.Model):
	__tablename__ = 'goal'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class IdCheckTbl(db.Model):
	__tablename__ = 'id_check'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

	@hybrid_property
	def password(self):
		return self.employee_id

	@password.setter
	def set_password(self, password):
		self.employee_id = argon2.generate_password_hash(password)

	def check_password(self, password):
		return argon2.check_password_hash(self.employee_id, password)


class LevelsTbl(db.Model):
	__tablename__ = 'levels'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class LibraryTbl(db.Model):
	__tablename__ = 'library'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
# Query Factory for form QuerySelect field
def getLibraries():
	libraries = LibraryTbl.query.order_by(LibraryTbl.library_name).all()
	return libraries


class LoginInfoTbl(db.Model, UserMixin):
	__tablename__ = 'login_info'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

	@hybrid_property
	def password(self):
		return self.password_hash

	@password.setter
	def set_password(self, password):
		self.password_hash = argon2.generate_password_hash(password)

	def check_password(self, password):
		return argon2.check_password_hash(self.password_hash, password)

	def get_id(self):
		   return (self.uuid)


class PrizeTbl(db.Model):
	__tablename__ = 'prize'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	
class ReaderTbl(db.Model):
	__tablename__ = 'reader'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class ReaderArchiveTbl(db.Model):
	__tablename__ = 'reader_archive'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
class ReaderProgressTbl(db.Model):
	__tablename__ = 'reader_progress'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class SchoolTbl(db.Model):
	__tablename__ = 'school'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

# Query Factory for form QuerySelect field
def getSchools():
	schools = SchoolTbl.query.order_by(SchoolTbl.school_name).all()
	return schools

class SchoolDistrictTbl(db.Model):
	__tablename__ = 'school_district'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class StaffTbl(db.Model):
	__tablename__ = 'staff'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

class UserInfoTbl(db.Model):
	__tablename__ = 'user_info'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}

# State & Zip Code database table adapted from SimpleMaps
# https://simplemaps.com/data/us-zips
# Used under a Creative Commons Attribution 4.0 International (CC BY 4.0) license
# https://creativecommons.org/licenses/by/4.0/
class ZipTbl(db.Model):
	__tablename__ = 'state_zip'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
# Query Factory for form QuerySelect field
def getStates():
	states = ZipTbl.query.order_by(ZipTbl.state_name).distinct(ZipTbl.state_name)
	return states

class LibraryStatsVw(db.Model):
	__tablename__ = 'library_statistics'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	library = db.Column(db.String, primary_key=True)
	
class PrizeLevelVw(db.Model):
	__tablename__ = 'prize_level'
	__table_args__ = (
		db.PrimaryKeyConstraint(
			'prize_uuid', 
			'reader_level'
		),
		{
			'autoload':True,
			'autoload_with': db.engine
		}
	)
class ReaderAgeLevelVw(db.Model):
	__tablename__ = 'reader_age_level'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	reader_uuid = db.Column(postgresql.UUID, primary_key=True)

class ReaderGoalVw(db.Model):
	__tablename__ = 'reader_goal'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	reader_uuid = db.Column(postgresql.UUID, primary_key=True)

class ReaderInfoCompVw(db.Model):
	__tablename__ = 'reader_info_composite'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	reader_uuid = db.Column(postgresql.UUID, primary_key=True)

class SummStatsVw(db.Model):
	__tablename__ = 'summary_statistics'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	total_readers = db.Column(db.Integer, primary_key=True)

class ZipServiceVw(db.Model):
	__tablename__ = 'zip_service_library'
	__table_args__ = {
		'autoload':True,
		'autoload_with': db.engine
	}
	library_name = db.Column(db.String, primary_key=True)
