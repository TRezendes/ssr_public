# Staff - Blueprint for staff interaction with the app

from flask import Blueprint
from flask_login import current_user


staff = Blueprint('staff', __name__, template_folder='templates', static_folder='static')

from . import staff_routes
