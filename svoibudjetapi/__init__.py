import logging.config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from svoibudjetapi.support import CustomJSONEncoder

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.json_encoder = CustomJSONEncoder
logging.config.dictConfig(app.config.get('LOGGING', {'version': 1}))
db = SQLAlchemy(app)

import svoibudjetapi.views
import svoibudjetapi.models
import svoibudjetapi.commands
