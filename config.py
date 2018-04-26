import os, json


def get_json_env(env, instance=list, default=[]):
    try:
        value = json.loads(os.environ[env])
        if isinstance(value, instance): return value
    except json.decoder.JSONDecodeError: pass
    except KeyError: pass
    return default


class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Temporary directory
    TEMP_DIR = os.getenv('TEMP_DIR') or \
        os.path.join(BASE_DIR, 'tmp')
    # Logs directory
    LOGS_DIR = os.getenv('LOGS_DIR') or \
        os.path.join(BASE_DIR, 'log')
    # Log filename
    LOG_FILENAME = os.getenv('LOG_FILENAME') or \
        os.path.join(LOGS_DIR, 'app.log')
    # Log format
    LOG_FORMAT = os.getenv('LOG_FORMAT') or \
        "%(asctime)s {%(module)s:%(lineno)d} %(levelname)s - %(message)s"
    # Log level
    LOG_LEVEL = os.getenv('LOG_LEVEL') or 'ERROR'
    # Log file maxBytes
    LOG_MAXBYTES = 10000000
    # Debug mode
    DEBUG = False
    # Define the database - we are working with
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_CONNECT_OPTIONS = {}
    # Flashes
    FLASHES = get_json_env('FLASHES')

    SECRET_KEY = os.getenv('SECRET_KEY') or 'tvservice'

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    MAIL_SUBJECT_PREFIX = os.getenv('MAIL_SUBJECT_PREFIX') or 'TVService'
    MAIL_SENDER = os.getenv('MAIL_SENDER') or ADMIN_EMAIL
    MAIL_SERVER = os.getenv('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or ADMIN_EMAIL
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    NORMALIZE_SUBREG = [(''':|;|"|'|`|!|\?|\.|,|\[|\]|\(|\)|\s+''', ''), (r'\s+', ' '), ('ё', 'е')]
    CHANNEL_ACTIVE_GROUP = 17

    @staticmethod
    def init_app(app):
        if not os.path.exists(app.config['TEMP_DIR']):
            os.makedirs(app.config['TEMP_DIR'])
        if not os.path.exists(app.config['LOGS_DIR']):
            os.makedirs(app.config['LOGS_DIR'])

    @staticmethod
    def get_json_env(env, instance=list, default=[]):
        try:
            value = json.loads(os.environ[env])
            if isinstance(value, instance): return value
        except json.decoder.JSONDecodeError: pass
        except KeyError: pass
        return default


class DevelopmentConfig(Config):
    FLASHES = [('Development mode','warning')]
    LOG_LEVEL = 'DEBUG'
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/tvservice'
    #SERVER_NAME = os.getenv('SERVER_NAME') or '192.168.0.2:5000'


class TestingConfig(Config):
    FLASHES = [('Testing mode','warning')]
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
