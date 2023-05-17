"""
Copyright (c) 2022 Timothy Rezendes

This file is part of Simple Summer Reading.

Simple Summer Reading is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Foobar is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Simple Summer Reading. If not, see <https://www.gnu.org/licenses/>.
"""

from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_argon2 import Argon2
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import json

db = SQLAlchemy()
argon2 = Argon2()
csrf = CSRFProtect()
login_manager = LoginManager()

def bad_request_error(e):
    return render_template('400.html'), 400
def forbidden_error(e):
    return render_template('403.html'), 403
def page_not_found_error(e):
    return render_template('404.html'), 404
def method_not_allowed_error(e):
    return render_template('405.html'), 405
def server_error(e):
    return render_template('500.html'), 500

def create_app():
    app = Flask(__name__)
    config_path = 'config.json'
    with open(config_path) as config_file:
        config = json.load(config_file)

    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = config.get('DEV_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    db.init_app(app)
    db.app = app

    argon2.init_app(app)
    argon2.app = app

    csrf.init_app(app)
    csrf.app = app

    login_manager.init_app(app)
    login_manager.app = app

    login_manager.session_protection = 'strong'
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'


    # Register blueprints
    from .auth import auth as auth
    from .reader import reader as reader
    from .staff import staff as staff
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(reader, url_prefix='/reader')
    app.register_blueprint(staff, url_prefix='/staff')

    # Register error handlers
    app.register_error_handler(400, bad_request_error)
    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(404, page_not_found_error)
    app.register_error_handler(405, method_not_allowed_error)
    app.register_error_handler(500, server_error)

    # Is this thing on?
    @app.route('/232')
    def its_alive():
        return render_template('itsAlive.html')

    @app.route('/page_check/<page>')
    def page_check(page):
        return render_template(page)

    @app.route('/')
    def landing():
        return redirect(url_for('auth.login'))


    return app
