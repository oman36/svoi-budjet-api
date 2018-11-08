import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from svoibudjetapi.support import CustomJSONEncoder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ROOT_DIR'] = os.path.dirname(os.path.abspath(__file__))
app.config['LOG_DIR'] = os.environ.get('LOG_DIR', os.path.join(app.config['ROOT_DIR'], 'logs'))
app.config['PROVERKACHEKA_USER'] = os.environ.get('PROVERKACHEKA_USER')
app.config['PROVERKACHEKA_PASS'] = os.environ.get('PROVERKACHEKA_PASS')
app.config['JSON_FILES_DIR'] = os.environ.get('JSON_FILES_DIR', app.config['ROOT_DIR'])
app.json_encoder = CustomJSONEncoder

db = SQLAlchemy(app)

import svoibudjetapi.views
import svoibudjetapi.models
import svoibudjetapi.commands
