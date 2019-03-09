import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.environ.get('LOG_DIR', os.path.join(ROOT_DIR, 'logs'))
PROVERKACHEKA_USER = os.environ.get('PROVERKACHEKA_USER')
PROVERKACHEKA_PASS = os.environ.get('PROVERKACHEKA_PASS')
JSON_FILES_DIR = os.environ.get('JSON_FILES_DIR', ROOT_DIR)
if 'DADATA_KEY' in os.environ:
    DADATA_KEY = os.environ.get('DADATA_KEY')
MEDIA_DIR = os.path.join(ROOT_DIR, 'media')
DAEMON_SLEEP = 5
LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)8s %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
        },
        'debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'backupCount': 100,
            'maxBytes': 2097152,
            'level': 'DEBUG',
            'formatter': 'default',
        },
        'info': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'info.log'),
            'backupCount': 100,
            'maxBytes': 2097152,
            'level': 'INFO',
            'formatter': 'default'
        },
        'warning': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'warning.log'),
            'backupCount': 100,
            'maxBytes': 2097152,
            'level': 'WARNING',
            'formatter': 'default'
        },
        'error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'error.log'),
            'backupCount': 100,
            'maxBytes': 2097152,
            'level': 'ERROR',
            'formatter': 'default'
        },
        'critical': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'critical.log'),
            'backupCount': 100,
            'maxBytes': 2097152,
            'level': 'CRITICAL',
            'formatter': 'default'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG' if os.environ.get('DEBUG') or os.environ.get('FLASK_DEBUG') else 'INFO',
            'propagate': 'no',
            'handlers': ['debug', 'info', 'warning', 'error', 'critical'],
        },
    },
    'root': {
        'level': 'DEBUG' if os.environ.get('DEBUG') or os.environ.get('FLASK_DEBUG') else 'INFO',
        'handlers': ['debug', 'info', 'warning', 'error', 'critical'],
    }
}
