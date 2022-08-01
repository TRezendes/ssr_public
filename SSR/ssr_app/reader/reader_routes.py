from flask import Blueprint, flash, render_template, redirect, session, url_for
from SSR.ssr_app.models import ActivityTbl, CompActsTbl, LibraryTbl, LoginInfoTbl, PrizeTbl, ReaderTbl, ReaderProgressTbl, SchoolTbl, StaffTbl, UserInfoTbl, ZipTbl, PrizeLevelVw, ReaderAgeLevelVw, ReaderGoalVw
from .reader_forms import DeleteReaderForm, ProgressForm, ReaderRegForm
from wtforms.validators import ValidationError
from flask_login import current_user, login_required, login_user, logout_user
from SSR.ssr_app import db, login_manager
from datetime import timedelta
from uuid import uuid4
from . import reader
import random

@login_manager.user_loader
def user_loader(user_id):
	return LoginInfoTbl.query.get(user_id)


@reader.route('/index', methods=['GET', 'POST'])
@reader.route('/', methods=['GET', 'POST'])
@login_required
def index():
	login_obj = LoginInfoTbl.query.filter_by(username=current_user.username).first()
	# Set the session Global Staff Variable  for use in templates throughout the session
	if StaffTbl.query.filter_by(user_id=login_obj.uuid).first():
		staff_role = StaffTbl.query.filter_by(user_id=login_obj.uuid).with_entities(StaffTbl.staff_role).first()[0]
		if staff_role == 'Administrator':
			session['gsv'] = 'admin'
		else:
			session['gsv'] = 'staff'
	else:
		session['gsv'] = None
		staff_role = None
	user_obj = UserInfoTbl.query.filter_by(user_id=login_obj.uuid).first()
	Fname, email, phone = user_obj.full_name_user, user_obj.email_address_user, user_obj.phone_number_user
	session['fname'] = Fname
	reader_obj = ReaderTbl.query.filter_by(user_id=login_obj.uuid).order_by(ReaderTbl.date_of_birth).all()
	# Query for and collect various variables for use in the template
	for reader in reader_obj:
		reader.age = ReaderAgeLevelVw.query.filter_by(reader_uuid=reader.reader_uuid).first().age
		reader.level = ReaderAgeLevelVw.query.filter_by(reader_uuid=reader.reader_uuid).first().reader_level
		reader.questions=0
		reader_check=ReaderProgressTbl.query.filter_by(reader_uuid=reader.reader_uuid).first()
		reader.books=reader_check.books_read
		reader.time=reader_check.time_read
		reader.complete=reader_check.goals_completed
		reader.activities=reader_check.activities_completed
		# Count up the number of questions each reader has answered
		if reader_check.answer_1:
			reader.questions += 1
		if reader_check.answer_2:
			reader.questions += 1
		if reader_check.answer_3:
			reader.questions += 1
		if reader.level == 2 and reader.questions >= 3:
			questions=3
		if reader.level == 3 or reader.level == 4:
			if reader.questions >= 2:
				reader.questions = 2
	return render_template(
		'reader/reader_index.html',
		Fname=Fname,
		email=email,
		phone=phone,
		staff_role=staff_role,
		reader_obj=reader_obj
		)

@reader.route('/reg', methods=['GET', 'POST'])
@login_required
def reader_reg():
	form=ReaderRegForm()
	if form.validate_on_submit():
		if form.school1.data:
			school_selection=form.school1.data.school_name
		else:
			school_selection=None
		new_reader = ReaderTbl(
			reader_uuid=str(uuid4()),
			user_id=current_user.uuid,
			reader_school=school_selection,
			full_name_reader=form.name.data,
			date_of_birth=form.dob.data,
			mailing_address_reader=form.mailing_address.data,
			city_reader=form.city.data,
			state_abbr_reader=form.state.data.state_id,
			zip5_reader=form.zip5.data,
			zip4_reader=form.zip4.data
		)
		db.session.add(new_reader)
		db.session.commit()
		flash(f'Reader {new_reader.full_name_reader} created successfully!', category='success')
		return redirect(url_for('reader.index'))
	return render_template(
		'/reader/reader_reg.html',
		form=form
	)

@reader.route('/progress/<ruuid>/<rname>', methods=['GET', 'POST'])
@login_required
def progress_page(ruuid, rname):
	form=ProgressForm()
	delete_form=DeleteReaderForm()
	# Get Reader Level from database
	rlevel=ReaderAgeLevelVw.query.filter_by(reader_uuid=ruuid).first().reader_level
	# Get object from database containing all activities
	activity_obj=ActivityTbl.query.filter_by(reader_level=rlevel).order_by(ActivityTbl.activity_uuid).all()
	# Get object from database containing all reader goals for current reader
	goal_obj=ReaderGoalVw.query.filter_by(reader_uuid=ruuid).first()
	# Initialize Progress Object
	prog_obj=None
	# Get questions from Goal Object and assign them to variables for printing in template
	gq1, gq2, gq3 = None, None, None
	if goal_obj.question_1:
		gq1=goal_obj.question_1
	if goal_obj.question_2:
		gq2=goal_obj.question_2
	if goal_obj.question_3:
		gq3=goal_obj.question_3
	# Get object from database containing progress-to-date for current reader
	currents=ReaderProgressTbl.query.filter_by(reader_uuid=ruuid).first()
	# Initialize progress-to-date variables at 0
	pct_books, pct_time, cur_books, cur_acts, cur_time=0, 0, 0, 0, timedelta(seconds=0)
	acts_dict = {'act1': False, 'act2': False, 'act3': False, 'act4': False, 'act5': False, 'act6': False, 'act7': False, 'act8': False, 'act9': False, 'act10': False, 'act11': False, 'act12': False}
	# Initialize list of activities for later iteration
	acts_list = list(acts_dict.keys())
	# If we're here to delete a reader, here's where it happens. Database trigger handles archiving.
	if delete_form.delete.data:
		print('BALEETED!') # https://www.youtube.com/watch?v=07h0ksKx5sM
		reader_to_delete=ReaderTbl.query.get(ruuid)
		db.session.delete(reader_to_delete)
		db.session.commit()
		# Having deleted the reader record, return to the index page
		return redirect(url_for('reader.index'))
	# Set progress-to-date variables from progress-to date object
	complete_flag=currents.goals_completed
	cur_time=currents.time_read
	cur_books=currents.books_read
	cur_acts=currents.activities_completed
	# Set goal variables from Goal Object
	goal_books=goal_obj.books_to_read
	goal_time=goal_obj.minutes_to_read
	# Until we check, we assume the reader hasn't met any of their goals (initialize flag variables)
	act_flag, book_flag, time_flag = False, False, False
	# That said, if they don't have an assigned number of books or amount of time to read, they pass that check by default
	if goal_books == 0:
		book_flag = True
	if goal_time == timedelta(seconds=0):
		time_flag = True
	# Calculate the percentage completed of books-to-read or time-to-read goals and check if they've met their reading goal
	if goal_books > 0:
		pct_books=int((cur_books/goal_books)*100)
		if cur_books >= goal_books:
			book_flag = True
	if goal_time > timedelta(seconds=0):
		pct_time=int((cur_time/goal_time)*100)
		if cur_time >= goal_time:
			time_flag = True
	# Check the completed_activities table to see which activities have been completed; acts_dict is used in template to mark completed activities on the progress page
	for index, act in enumerate(activity_obj):
		act_bool = CompActsTbl.query.filter_by(activity_uuid=act.activity_uuid, reader_uuid=ruuid).first()
		if act_bool:
			acts_dict[acts_list[index]] = True
	# Add up the number of completed activities to see if that goal has been acheived
	if sum(acts_dict.values()) >= goal_obj.number_of_activities:
		act_flag = True
	# Because the number of questions to answer varies, we'll start by assuming that all the question goals have been met and then evaluate  the actual state as we go
	q1_flag, q2_flag, q3_flag = True, True, True
	# If they have to answer the question, assume they haven't met the goal
	if goal_obj.question_1:
		q1_flag = False
		# But if they have answered it, then mark the goal as achieved
		if currents.answer_1:
			q1_flag = True
	if goal_obj.question_2:
		q2_flag = False
		if currents.answer_2:
			q2_flag = True
	if goal_obj.question_3:
		q3_flag = False
		if currents.answer_3:
			q3_flag = True
	# Check each flag in turn. If they're all True, then set the overall completion flag as well
	if act_flag:
		if book_flag:
			if time_flag:
				if q1_flag:
					if q2_flag:
						if q3_flag:
							complete_flag = True
	### Define function to concatenate time entry value & units into interval data for DB insert ###
	def TimeRead(time, units):
		if form.time_entry.data:
			if units == 'Minutes':
				time_read=timedelta(minutes = time)
			if units == 'Hours':
				time_read=timedelta(hours = time)
		else:
			time_read = timedelta(seconds = 0)
		return time_read
	### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
	
	# If new progress has been entered and submitted…
	if form.validate_on_submit():
		# True/False list from activity check boxes
		check_list = [form.activity_check1.data, form.activity_check2.data, form.activity_check3.data, form.activity_check4.data, form.activity_check5.data, form.activity_check6.data, form.activity_check7.data, form.activity_check8.data, form.activity_check9.data, form.activity_check10.data, form.activity_check11.data, form.activity_check12.data]
		# Get the identifier for all newly completed activities and add them to completed_activities table
		# Level 2 & 3 have fewer activities than Level 4 which in turn has fewer activities than Level 1
		new_comp_list = []
		for i, box in enumerate(check_list):
			if rlevel == 'Level 2' or rlevel == 'Level 3':
				if i > 9:
					break
			if rlevel == 'Level 4' and i > 10:
				break
			actID = activity_obj[i].activity_uuid
			if CompActsTbl.query.filter_by(activity_uuid=actID, reader_uuid=ruuid).first() != True:
				if check_list[i]:
					comp_dict = {'reader_uuid': ruuid, 'activity_uuid': actID}
					new_comp_list.append(comp_dict)
		# Take that list of all the newly completed activities and generate a record object for each activity in it, then add those records to the SQLAlchemy session for later commission to the database.
		comp_obj_list = []
		for record in new_comp_list:
			comp_obj = CompActsTbl(**record)
			comp_obj_list.append(comp_obj)
		db.session.add_all(comp_obj_list)
		# Get current reader's Progress Object from the database
		prog_obj=ReaderProgressTbl.query.get(ruuid)
		# Add current reader's new progress to their progress-to-date
		prog_obj.time_read=TimeRead(form.time_entry.data, form.time_unit.data) + cur_time
		# Addition will fail if no number of books has been entered on the form. The TimeRead function handles the equivalent check for the line above
		if form.books_entry.data:
			prog_obj.books_read=form.books_entry.data + cur_books
		prog_obj.activities_completed=sum(check_list) + cur_acts
		# If the reader has already answered the question, keep that answer, otherwise add the new answer from the form to the Progress Object
		if prog_obj.answer_1:
			prog_obj.answer_1=prog_obj.answer_1
		else:
			prog_obj.answer_1=form.answer_1.data
		if prog_obj.answer_2:
			prog_obj.answer_2=prog_obj.answer_2
		else:
			prog_obj.answer_2=form.answer_2.data
		if prog_obj.answer_3:
			prog_obj.answer_3=prog_obj.answer_3
		else:
			prog_obj.answer_3=form.answer_3.data
		# Set the complete flag on the Progress Object to update the completed status in the database
		prog_obj.goals_completed=complete_flag
		# Commit the SQLAlchemy session to add the updated Progress Object back to the database
		db.session.commit()
		flash('Reading progress successfully logged.', category='success')
		return redirect(
			url_for(
				'reader.progress_page',
				ruuid=ruuid,
				rname=rname
				)
			)
	# The template needs the Progress Object and Home Library even if we haven't submitted the form
	prog_obj=prog_obj=ReaderProgressTbl.query.get(ruuid)
	home_library=ReaderTbl.query.filter_by(reader_uuid=ruuid).with_entities(ReaderTbl.home_library).first()[0]
	# Is the Reader from a local library's service area?
	in_area = False
	if home_library in LibraryTbl.query.with_entities(LibraryTbl.library_name).all():
		in_area = True
	return render_template(
		'/reader/progress.html',
		gq1=gq1,
		gq2=gq2,
		gq3=gq3,
		form=form,
		rname=rname,
		ruuid=ruuid,
		rlevel=rlevel,
		in_area=in_area,
		prog_obj=prog_obj,
		cur_time=cur_time,
		pct_time=pct_time,
		cur_acts=cur_acts,
		cur_books=cur_books,
		pct_books=pct_books,
		acts_dict=acts_dict,
		acts_list=acts_list,
		delete_form=delete_form,
		home_library=home_library,
		activity_obj=activity_obj,
		complete_flag=complete_flag
	)
	
	
	

@reader.route('/prizes/<ruuid>/<rname>')
def prizes(ruuid, rname):
	# For a personalized potential prize experience
	# Displays only the prizes appropriate to the Current Reader's Level
	if current_user.is_authenticated:
		ruuid=ruuid
		rname=rname
		rlevel=ReaderAgeLevelVw.query.filter_by(reader_uuid=ruuid).with_entities(ReaderAgeLevelVw.reader_level).first()[0]
		prize_obj=PrizeLevelVw.query.filter_by(reader_level=rlevel).all()
		return render_template(
		'/reader/prizes.html',
		ruuid=ruuid,
		rname=rname,
		prize_obj=prize_obj
	)
	# Johnny, tell then what they can win!
	prize_obj=PrizeLevelVw.query.distinct(PrizeLevelVw.prize_uuid).all()
	# Randomize which and what order prizes appear on the page for users who aren't logged in.
	random.shuffle(prize_obj)
	randalorian=prize_obj[0:12] # This is the (randomized) way…
	print(randalorian)
	print(type(randalorian))
	return render_template(
	'/reader/prizes.html',
	randalorian=randalorian,
	ruuid=ruuid,
	rname=rname
	
)