import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.environ.get('LOG_DIR', os.path.join(ROOT_DIR, 'logs'))
PROVERKACHEKA_USER = os.environ.get('PROVERKACHEKA_USER')
PROVERKACHEKA_PASS = os.environ.get('PROVERKACHEKA_PASS')
JSON_FILES_DIR = os.environ.get('JSON_FILES_DIR', ROOT_DIR)
DADATA_KEY = os.environ.get('DADATA_KEY')
