import logging
import time

from proverkacheka.api import API
from proverkacheka.exceptions import ProverkachekaBaseException

from svoibudjetapi import app, db
from svoibudjetapi.models import QRString
from svoibudjetapi.support.json_handler import save_check_json, save_check_from_json

logger = logging.getLogger(__name__)


@app.cli.command()
def fetch_json():
    logger.debug('Start.')
    api = API(
        username=app.config['PROVERKACHECKA_USER'],
        password=app.config['PROVERKACHECKA_PASS'],
    )
    while True:
        logger.debug('Iteration begin.')
        try:
            step_size = 5
            offset = 0
            while True:
                next_strings = QRString.query\
                    .filter(QRString.check_id.is_(None))[offset:offset + step_size]

                offset += step_size

                logger.debug('Count of next strings : %d.', len(next_strings))
                if len(next_strings) == 0:
                    break

                for next_string in next_strings:  # type:QRString
                    if not next_string.is_valid:
                        try:
                            logger.debug('Checking if "%s" is valid.', next_string.qr_string)
                            next_string.is_valid = api.check_ticket(next_string.qr_string)
                        except ProverkachekaBaseException:
                            logger.debug('next_string is_valid checking.', exc_info=True)
                            continue

                        db.session.commit()

                    if not next_string.is_valid:
                        logger.debug('"%s" is not valid.', next_string.qr_string)
                        continue

                    try:
                        json_string = api.get_ticket_json_text(next_string.qr_string)
                    except ProverkachekaBaseException:
                        logger.debug('Getting json.', exc_info=True)
                        continue

                    try:
                        save_check_json(json_string, next_string.id)
                    except OSError:
                        logger.exception('Save check json.')

                    check = save_check_from_json(json_string)

                    next_string.check = check
                    db.session.commit()
        except:
            logger.exception('')

        time.sleep(app.config['DAEMON_SLEEP'])
