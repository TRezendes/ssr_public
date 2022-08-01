from flask import abort, Blueprint, flash, render_template, redirect, Response, request, session, url_for
from SSR.ssr_app.models import LibraryTbl, LoginInfoTbl, ReaderTbl, StaffTbl, UserInfoTbl, LibraryStatsVw, ReaderAgeLevelVw, ReaderInfoCompVw, SummStatsVw
from flask_login import current_user, login_required, login_user, logout_user
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from .staff_forms import StatForm
from matplotlib.figure import Figure
import numpy as np
import datetime
import io
from datetime import timedelta
from string import Formatter
from SSR.ssr_app import db, login_manager
from . import staff



@login_manager.user_loader
def user_loader(user_id):
	return LoginInfoTbl.query.get(user_id)


# This magnificent function comes from  https://stackoverflow.com/a/42320260/16832874
# It was written by user MarredCheese (https://stackoverflow.com/users/5405967/marredcheese),
# based on work by user mpounsett (https://stackoverflow.com/users/951589/mpounsett).
def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
	"""Convert a datetime.timedelta object or a regular number to a custom-
	formatted string, just like the stftime() method does for datetime.datetime
	objects.

	The fmt argument allows custom formatting to be specified.  Fields can
	include seconds, minutes, hours, days, and weeks.  Each field is optional.

	Some examples:
		'{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
		'{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
		'{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
		'{H}h {S}s'                       --> '72h 800s'

	The inputtype argument allows tdelta to be a regular number instead of the
	default, which is a datetime.timedelta object.  Valid inputtype strings:
		's', 'seconds',
		'm', 'minutes',
		'h', 'hours',
		'd', 'days',
		'w', 'weeks'
	"""

	# Convert tdelta to integer seconds.
	if inputtype == 'timedelta':
		remainder = int(tdelta.total_seconds())
	elif inputtype in ['s', 'seconds']:
		remainder = int(tdelta)
	elif inputtype in ['m', 'minutes']:
		remainder = int(tdelta)*60
	elif inputtype in ['h', 'hours']:
		remainder = int(tdelta)*3600
	elif inputtype in ['d', 'days']:
		remainder = int(tdelta)*86400
	elif inputtype in ['w', 'weeks']:
		remainder = int(tdelta)*604800

	f = Formatter()
	desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
	possible_fields = ('W', 'D', 'H', 'M', 'S')
	constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
	values = {}
	for field in possible_fields:
		if field in desired_fields and field in constants:
			values[field], remainder = divmod(remainder, constants[field])
	return f.format(fmt, **values)

	###


@staff.route('/index', methods=['GET', 'POST'])
@staff.route('/', methods=['GET', 'POST'])
@login_required
def index():
	# Only Staff are authorized for this page. If the current user is not staff, return an HTTP 403 error
	staff_obj=StaffTbl.query.filter_by(user_id=current_user.uuid).first()
	if staff_obj:
		pass
	else:
		abort(403)
	form=StatForm()
	# The righthand stat block defaults to the Current User's place of employment…
	if request.method=='GET':
		selected_library=staff_obj.employer
	# …but a dropdown select field allows the user to select any library to view statistics for.
	if request.method=='POST' and form.validate_on_submit():
		selected_library=form.library_select.data.library_name
	user_obj=UserInfoTbl.query.filter_by(user_id=current_user.uuid).first()
	library_obj=LibraryTbl.query.filter_by(library_name=staff_obj.employer).first()
	summ_stats_obj=SummStatsVw.query.first()
	lib_stats_obj=LibraryStatsVw.query.filter_by(library=selected_library).first_or_404()
	date=datetime.date.today()
	tot_time=summ_stats_obj.total_time_read
	avg_time=summ_stats_obj.average_time_read
	# Use the 'strfdelta' function to conditionally format display of the time stats to make them easy to read no matter the duration
	if lib_stats_obj.total_time_read:
		tot_lib_time=lib_stats_obj.total_time_read
	else:
		tot_lib_time=timedelta(seconds=0)
	if tot_time < timedelta(hours=1):
		fmt1='{M}m {S}s'
	elif tot_time >= timedelta(hours=1) and tot_time < timedelta(hours=24):
		fmt1='{H}h {M}m'
	elif tot_time >= timedelta(hours=24) and tot_time < timedelta(hours=168):
		fmt1='{D}d {H}h {M}m'
	else:
		fmt1='{W}w {D}d {H}h {M}m'
	if avg_time < timedelta(hours=1):
		fmt2='{M}m {S}s'
	elif avg_time >= timedelta(hours=1) and tot_time < timedelta(hours=24):
		fmt2='{H}h {M}m'
	elif avg_time >= timedelta(hours=24) and tot_time < timedelta(hours=168):
		fmt2='{D}d {H}h {M}m'
	else:
		fmt2='{W}w {D}d {H}h {M}m'
	if tot_lib_time < timedelta(hours=1):
		fmt3='{M}m {S}s'
	elif tot_lib_time >= timedelta(hours=1) and tot_time < timedelta(hours=24):
		fmt3='{H}h {M}m'
	elif tot_lib_time >= timedelta(hours=24) and tot_time < timedelta(hours=168):
		fmt3='{D}d {H}h {M}m'
	else:
		fmt3='{W}w {D}d {H}h {M}m'
	tot_time=strfdelta(tot_time, fmt1)
	avg_time=strfdelta(avg_time, fmt2)
	tot_lib_time=strfdelta(tot_lib_time, fmt3)
	return render_template(
		'staff/staff_index.html',
		date=date,
		form=form,
		tot_time=tot_time,
		avg_time=avg_time,
		user_obj=user_obj,
		staff_obj=staff_obj,
		library_obj=library_obj,
		tot_lib_time=tot_lib_time,
		lib_stats_obj=lib_stats_obj,
		summ_stats_obj=summ_stats_obj,
		selected_library=selected_library
	)


# Based on example code at:
# https://www.tutorialspoint.com/how-to-show-matplotlib-in-flask,
# https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py,
# and https://stackoverflow.com/questions/10369681/how-to-plot-bar-graphs-with-same-x-coordinates-side-by-side-dodged
@staff.route('/charts/<chart>')
@login_required
# This route dynamically generates charts based on information in the database and outputs them as PNG images suitable for embedding with the <img /> tag
def charts(chart):
	# Only Staff are authorized for this route. If the current user is not staff, return an HTTP 403 error
	staff_obj=StaffTbl.query.filter_by(user_id=current_user.uuid).first()
	if staff_obj:
		pass
	else:
		abort(403)
	# This line, apparently, is necessary to keep Python from going out in a blaze of window-management-error glory
	matplotlib.pyplot.switch_backend('Agg')
	if chart == 'histogram-age':
		hist_data=ReaderAgeLevelVw.query.with_entities(ReaderAgeLevelVw.age).all()
		age_list=[]
		# In testing, my son entered a reader who was 2000 years old. There were problems. According to Wikipedia (https://en.wikipedia.org/wiki/List_of_the_verified_oldest_people), the oldest verified living person ever was 122 & 1/2 years old. That seems like a fair limit for the graph.
		for row in hist_data:
			if row[0] < 123:
				age_list.append(row[0])
		title = 'Readers by Age'
		def Histogram(data, title):
			counts = np.bincount(data)
			# Limiting the size beyond even the data age limit is also important
			x_size=min([max(data)/2, 15])
			y_size=max(counts)/2
			if y_size > x_size:
				y_size=x_size
			fig = Figure(figsize=(x_size, y_size))
			axis = fig.add_subplot(1, 1, 1)
			axis.bar(range(max(data)+1), counts, width=1, align='center', color='#222255', edgecolor='#9a9aba')
			axis.set(xticks=range(max(data)+1), xlim=[-1, max(data) + 1])
			output = io.BytesIO()
			FigureCanvas(fig).print_png(output)
			return Response(output.getvalue(), mimetype='image/png')
		return Histogram(age_list, title)
	if chart == 'bar-readers':
		bar_data=LibraryStatsVw.query.with_entities(LibraryStatsVw.library, LibraryStatsVw.total_readers, LibraryStatsVw.readers_completed).all()
		title = 'Readers by Library'
		def BarChart(data, title):
			library_list, total_list, completed_list = [], [], []
			for tuple in data:
				if tuple[1] > 0:
					library_list.append(tuple[0])
					total_list.append(tuple[1])
					completed_list.append(tuple[2])
			# The Library names take up too much room on the plot. We all know we're talking about public libraries. If 'Library' or Public Library' appear at the end of the library name, this loop drops those words to save space.
			for i, lib in enumerate(library_list):
				split = lib.split()
				if split[-1] == 'Library':
					if split[-2] == 'Public':
						library_list[i] = library_list[i].rsplit(" ", 2)[0]
						continue
					library_list[i] = library_list[i].rsplit(" ", 1)[0]
				# The Mountville branch had to go and bury 'Public Library' in the middle of the name where the loop can't find it. They get a custom shortener.
				if lib == 'Lancaster Public Library – Mountville Branch':
					library_list[i] = 'LPL Mountville Branch'
			x_label_positions = np.arange(len(library_list))
			bar_width = 0.35
			x_size=len(library_list)/2
			y_size=max(total_list) 
			if y_size > (2 * x_size):
				y_size= (2 * x_size)
			fig, ax = plt.subplots()
			total_bars = ax.bar(x_label_positions - bar_width/2, total_list, bar_width, label='Enrolled Readers',color='#222255')
			completed_bars = ax.bar(x_label_positions + bar_width/2, completed_list, bar_width, label='Completed Readers ', color='#9a9aba')
			ax.set_xticks(x_label_positions, library_list, rotation=45, ha='right')
			ax.legend()
			fig.tight_layout()
			output = io.BytesIO()
			FigureCanvas(fig).print_png(output)
			return Response(output.getvalue(), mimetype='image/png')
		return BarChart(bar_data, title)
		
@staff.route('/completed-readers')
@login_required
def completed():
	# Only Staff are authorized for this page. If the current user is not staff, return an HTTP 403 error
	staff_obj=StaffTbl.query.filter_by(user_id=current_user.uuid).first()
	if staff_obj:
		pass
	else:
		abort(403)
	date=datetime.date.today()
	user_obj=UserInfoTbl.query.filter_by(user_id=current_user.uuid).first()
	library_obj=LibraryTbl.query.filter_by(library_name=staff_obj.employer).first()
	comp_reader_obj=ReaderInfoCompVw.query.filter_by(goals_completed=True, home_library=staff_obj.employer).all()
	for reader in comp_reader_obj:
		reader.name=ReaderTbl.query.filter_by(reader_uuid=reader.reader_uuid).with_entities(ReaderTbl.full_name_reader).first()[0]
		reader.user_id=ReaderTbl.query.filter_by(reader_uuid=reader.reader_uuid).with_entities(ReaderTbl.user_id).first()[0]
		reader.email=UserInfoTbl.query.filter_by(user_id=reader.user_id).with_entities(UserInfoTbl.email_address_user).first()[0]
		reader.phone=UserInfoTbl.query.filter_by(user_id=reader.user_id).with_entities(UserInfoTbl.phone_number_user).first()[0]
	return render_template(
		'staff/completed_readers.html',
		date=date,
		user_obj=user_obj,
		staff_obj=staff_obj,
		timedelta=timedelta,
		library_obj=library_obj,
		comp_reader_obj=comp_reader_obj
	)
	