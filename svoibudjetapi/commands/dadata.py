import json
import logging
import time

import requests

from svoibudjetapi import app, db
from svoibudjetapi.models import Shop

logger = logging.getLogger(__name__)


class _CompanyNameGetter:
    URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"

    def __init__(self, key: str):
        self.headers = {
            "Authorization": f"Token {key}",
            "Content-Type": "application/json",
        }

    def get_name(self, inn: str) -> str:
        data = json.dumps({"query": inn, "count": 1})
        response = requests.post(self.URL, data=data, headers=self.headers)
        if response.status_code != 200:
            logger.warn('Api returned status_code %d', response.status_code)

        try:
            r_data = response.json()
            name = r_data['suggestions'][0]['value2']
        except:
            logger.warn('Api returned invalid format: %s', response.text)
            raise
        return name


@app.cli.command()
def dadata():
    logger.debug('Start.')
    queryset = Shop.query.filter(Shop.name.in_(('unknown', '')))
    api = _CompanyNameGetter(app.config['DADATA_KEY'])
    while True:
        logger.debug('Iteration begin.')
        try:
            step_size = 5
            offset = 0

            while True:
                next_shops = queryset[offset:offset + step_size]

                offset += step_size

                logger.debug('Count of next shops : %d.', len(next_shops))
                if len(next_shops) == 0:
                    break

                for next_shop in next_shops:  # type:Shop
                    try:
                        logger.debug('Getting name for %s id=%d', next_shop, next_shop.id)
                        next_shop.name = api.get_name(next_shop.inn)
                    except:
                        logger.exception('get_name')
                        continue

                    db.session.commit()
        except:
            logger.exception('')

        time.sleep(app.config['DAEMON_SLEEP'])
