# Auth - Blueprint for handling authentication tasks

from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')

from . import auth_routes
