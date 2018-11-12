from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from svoibudjetapi.support import CustomJSONEncoder

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.json_encoder = CustomJSONEncoder

db = SQLAlchemy(app)

import svoibudjetapi.views
import svoibudjetapi.models
import svoibudjetapi.commands
