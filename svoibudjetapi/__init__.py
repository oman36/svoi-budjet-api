import logging.config
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from svoibudjetapi.support import CustomJSONEncoder

log_msgs = []
app = Flask(__name__)
app.config.from_pyfile('config.py')
try:
    app.config.from_pyfile('env_config.py')
except FileNotFoundError:
    log_msgs.append((logging.WARN, 'File env_config.py not found.'))
app.json_encoder = CustomJSONEncoder

if not os.path.exists(app.config['LOG_DIR']):
    log_msgs.append((logging.WARN, '%s was created for logs.', app.config['LOG_DIR']))
    os.makedirs(app.config['LOG_DIR'])

if 'LOGGING' in app.config:
    logging.config.dictConfig(app.config['LOGGING'])
else:
    logging.basicConfig()

logger = logging.getLogger(__name__)
for args in log_msgs:
    logger.log(*args)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import svoibudjetapi.views
import svoibudjetapi.models
import svoibudjetapi.commands
