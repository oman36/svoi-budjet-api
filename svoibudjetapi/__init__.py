import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from svoibudjetapi.support import CustomJSONEncoder

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_encoder = CustomJSONEncoder

db = SQLAlchemy(app)

import svoibudjetapi.views
import svoibudjetapi.models
