import datetime
import os
import time
import traceback

from proverkacheka.api import API
from proverkacheka.exceptions import ProverkachekaBaseException

from svoibudjetapi import app, db
from svoibudjetapi.models import QRString
from svoibudjetapi.support.json_handler import save_check_json, save_check_from_json


@app.cli.command()
def fetch_json():
    def log_exception():
        if not os.path.isdir(app.config.get('LOG_DIR')):
            os.makedirs(app.config.get('LOG_DIR'))

        with open(os.path.join(app.config.get('LOG_DIR'), 'errors.log'), 'a+') as f:
            f.write('-' * 20 + datetime.datetime.now().strftime(' %Y-%m-%d %H:%M:%S ') + '-' * 20 + '\n')
            f.write(traceback.format_exc(20))

    while True:
        try:
            step_size = 5
            offset = 0
            proverka_api = API(
                username=app.config.get('PROVERKACHECKA_USER'),
                password=app.config.get('PROVERKACHECKA_PASS'),
            )
            while True:
                next_strings = QRString.query\
                    .filter(QRString.check_id.is_(None))[offset:offset + step_size]

                offset += step_size

                if len(next_strings) == 0:
                    break

                for next_string in next_strings:  # type:QRString
                    if not next_string.is_valid:
                        try:
                            next_string.is_valid = proverka_api.check_ticket(next_string.qr_string)
                        except ProverkachekaBaseException:
                            continue

                        db.session.commit()

                    if not next_string.is_valid:
                        continue

                    try:
                        json_string = proverka_api.get_ticket_json_text(next_string.qr_string)
                    except ProverkachekaBaseException:
                        continue

                    try:
                        save_check_json(json_string, next_string.id)
                    except OSError:
                        log_exception()

                    check = save_check_from_json(json_string)

                    next_string.check = check
                    db.session.commit()
        except:
            log_exception()

        time.sleep(5)
