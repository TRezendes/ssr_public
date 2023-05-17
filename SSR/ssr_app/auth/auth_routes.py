"""
Copyright (c) 2022–2023 Timothy Rezendes

This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Simple Summer Reading is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from flask import abort, Blueprint, flash, redirect, render_template, request, session, url_for
from ssr_app.models import IdCheckTbl, LibraryTbl, LoginInfoTbl, StaffTbl, UserInfoTbl
from .auth_forms import FileForm, LoginForm, RegistrationForm, StaffRegForm
from wtforms.validators import ValidationError
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required, login_user, logout_user
from ssr_app import argon2, db, login_manager
from io import TextIOWrapper
import csv
from uuid import uuid4
from . import auth


@login_manager.user_loader
def user_loader(user_id):
	return LoginInfoTbl.query.get(user_id)

@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('reader.index'))
	form = LoginForm()
	if form.validate_on_submit():
		attempted_user = LoginInfoTbl.query.filter_by(username=form.username.data).first()
		if attempted_user and attempted_user.check_password(password=form.password.data):
			login_user(attempted_user)
			flash(f'Success! You are logged in as {attempted_user.username}', category='success')
			return redirect(url_for('reader.index'))
		else:
			flash('Username and password do not match! Please try again.', category='danger')

	return render_template(
		'/auth/login.html',
		form = form
	)

@auth.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('reader.index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		# If a User is registering as Staff, the variables from the form need to be held in the session so they can be passed to the next page
		if form.staff_bool:
			session['username']=form.username.data
			# The session cookie is tamper proof but not encrypted, so password is hashed BEFORE being stored in the session variable
			session['password_hash']=argon2.generate_password_hash(form.password1.data)
			session['full_name']=form.full_name.data
			session['email']=form.email_address.data
			session['phone']=form.phone_number.data
			# Check the employee ID entered against a list of pre-populated employee IDs to ensure that only actual staff can register as such
			if form.staff_id.data:
				checkrows = IdCheckTbl.query.all()
				for row in checkrows:
					if row.check_password(password=form.staff_id.data):
						session['staff_role']=row.staff_role
						session['staff_id']=argon2.generate_password_hash(form.staff_id.data)
						return redirect(url_for(
							'auth.staff_reg'
						)
					)
		new_login_info = LoginInfoTbl(
			uuid=str(uuid4()),
			username=form.username.data,
			password_hash=argon2.generate_password_hash(form.password1.data)
		)
		new_user_info = UserInfoTbl(
			user_id=new_login_info.uuid,
			full_name_user=form.full_name.data,
			email_address_user=form.email_address.data,
			phone_number_user=form.phone_number.data
		)
		db.session.add(new_login_info)
		db.session.add(new_user_info)
		db.session.commit()
		login_user(new_login_info)
		flash(f'Account created successfully! You are now logged in as {new_login_info.username}', category='success')
		return redirect(url_for('reader.index'))

	if form.errors != {}: #If there are  validation errors
		for err_msg in form.errors.values():
			flash(f'There was an error with creating a user: {err_msg}', category='danger')

	for fieldName, errorMessages in form.errors.items():
		for err in errorMessages:
			print(err)
	return render_template(
		'/auth/register.html',
		form = form
	)

@auth.route('/staff_registration', methods=['GET', 'POST'])
def staff_reg():
	form = StaffRegForm()
	form.employer.query = LibraryTbl.query.order_by(LibraryTbl.library_name).all()
	if form.validate_on_submit():
		new_login_info = LoginInfoTbl(
			uuid=str(uuid4()),
			username=session['username'],
			password_hash=session['password_hash']
		)
		new_user_info = UserInfoTbl(
			user_id=new_login_info.uuid,
			full_name_user=session['full_name'],
			email_address_user=session['email'],
			phone_number_user=session['phone']
		)
		if session['staff_role'] == 'admin':
			staff_role='Administrator'
		else:
			staff_role='Staff User'
		new_staff_info = StaffTbl(
			staff_id=session['staff_id'],
			user_id=new_login_info.uuid,
			staff_role=staff_role,
			employer=form.employer.data.library_name,
			job_title=form.job_title.data
		)
		db.session.add(new_login_info)
		db.session.add(new_user_info)
		db.session.commit()
		db.session.add(new_staff_info)
		db.session.commit()
		login_user(new_login_info)
		# Clear the session variables we set on the registration page; we don't need them anymore
		pop_keys=['username', 'password_hash', 'full_name', 'email', 'phone', 'staff_id', 'staff_role']
		[session.pop(key) for key in pop_keys]
		flash(f'Account created successfully! You are now logged in as {new_login_info.username}', category='success')
		return redirect(url_for('reader.index'))

	if form.errors != {}:
		for err_msg in form.errors.values():
			flash(f'There was an error with creating a user: {err_msg}', category='danger')

	for fieldName, errorMessages in form.errors.items():
		for err in errorMessages:
			print(err)
	return render_template(
	'/auth/staff_reg.html',
	form = form
)

@auth.route('/page_check/<page>')
def page_check(page):
	return render_template(page)

@auth.route('/logout')
@login_required
def logout_page():
	session.pop('gsv')
	session.pop('fname')
	logout_user()
	flash('You have been logged out.', category='info')
	return redirect(url_for('auth.login'))


# File upload code based on example code at:
# https://wtforms.readthedocs.io/en/3.0.x/fields/ & https://flask-wtf.readthedocs.io/en/1.0.x/form/#file-uploads
# CSV import based on GitHub Gist https://gist.github.com/dasdachs/69c42dfcfbf2107399323a4c86cdb791 by user dasdachs (https://gist.github.com/dasdachs)
@auth.route('/employee-upload', methods=['GET', 'POST'])
@login_required
def upload():
	staff_obj=StaffTbl.query.filter_by(user_id=current_user.uuid).first()
	# Only Administrators are authorized for this page. If the current user is not an admin user, return an HTTP 403 error
	if staff_obj and session['gsv']=='admin':
		pass
	else:
		abort(403)
	form = FileForm()
	if form.validate_on_submit():
		csv_file = form.file.data
		filename = secure_filename(csv_file.filename)
		csv_file = TextIOWrapper(csv_file, encoding='utf-8')
		csv_reader = csv.reader(csv_file, delimiter=',')
		id_dicts = []
		for row in csv_reader:
			# Employee IDs hare hashed for secure storage
			employee_id=argon2.generate_password_hash(row[0])
			staff_role=row[1]
			id_row = {'employee_id': employee_id, 'staff_role': staff_role}
			id_dicts.append(id_row)
		id_list = []
		for record in id_dicts:
			id_obj = IdCheckTbl(**record)
			id_list.append(id_obj)
		num_records = len(id_list)
		db.session.add_all(id_list)
		db.session.commit()
		if num_records==1:
			flash(f'{filename} imported successfully. One employee ID stored securely.', category='success')
		else:
			flash(f'{filename} imported successfully. {num_records} employee IDs stored securely.', category='success')
			return redirect(url_for('staff.index'))
	if form.errors != {}:
		for err_msg in form.errors.values():
			flash(f'There was an error importing the file: {err_msg}', category='danger')
	return render_template(
		'auth/employee_upload.html',
		form=form
		)
