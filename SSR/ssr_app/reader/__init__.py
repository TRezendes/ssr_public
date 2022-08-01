# Reader - Blueprint for patron interaction with the app

from flask import Blueprint
from flask_login import current_user


reader = Blueprint('reader', __name__, template_folder='templates', static_folder='static')

from . import reader_routes
