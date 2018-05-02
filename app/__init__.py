import os
import logging
import base64
from flask import Flask, Response, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from config import config


mail = Mail()
db = SQLAlchemy()
scheduler = APScheduler()


login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.request_loader
def load_user_from_request(request):
    from .models import User
    auth = request.args.get('key')
    if not auth: auth = request.headers.get('Authorization')
    if auth:
        auth = auth.replace('Basic ', '', 1)
        try:
            auth = base64.b64decode(auth).decode('utf8').split(':')
        except Exception:
            return None
        user = User.query.filter_by(username=auth[0]).first()
        if user and user.verify_password(auth[1]):
            return user
    return None


CONFIG = config[os.getenv('CONFIG') or 'default']


def create_app(configuration=CONFIG):
    app = Flask(__name__)
    app.config.from_object(configuration)

    configuration.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    init_blueprints(app)
    init_logger(app)
    init_errors(app)
    return app


def init_blueprints(app):
    # /app/main/__init__.py
    from .main import main as main_bp
    app.register_blueprint(main_bp)

    # /app/auth/__init__.py
    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    # /app/api/__init__.py
    from .api import api_bp as api_bp
    app.register_blueprint(api_bp)


def init_logger(app):
    from logging.handlers import RotatingFileHandler
    fh = RotatingFileHandler(app.config['LOG_FILENAME'],
        maxBytes=app.config['LOG_MAXBYTES'], backupCount=5)

    app.logger.addHandler(fh)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    formatter = logging.Formatter(app.config['LOG_FORMAT'])
    for h in app.logger.handlers:
        h.setLevel(app.config['LOG_LEVEL'])
        h.setFormatter(formatter)


def init_errors(app):
    def get_handler(code):
        path = request.path
        for bp_name, bp in app.blueprints.items():
            if bp.url_prefix and path.startswith(bp.url_prefix):
                handler = app.error_handler_spec.get(bp_name, {}).get(code)
                if handler: return tuple(handler.values())[0]
        handler = app.error_handler_spec.get('main', {}).get(code)
        if handler: return tuple(handler.values())[0]

    @app.errorhandler(400)
    def bad_request(error):
        handler = get_handler(400)
        return handler(error) if handler else Response('bad request', 400)

    @app.errorhandler(401)
    def unauthorized(error):
        handler = get_handler(401)
        return handler(error) if handler else redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(error):
        handler = get_handler(403)
        return handler(error) if handler else redirect(url_for('main.index'))

    @app.errorhandler(404)
    def not_found(error):
        handler = get_handler(404)
        return handler(error) if handler else Response('not found', 404)
