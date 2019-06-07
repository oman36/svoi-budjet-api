import json
import logging
import time

import requests

from svoibudjetapi import app, db
from svoibudjetapi.models import Shop, FailedShopName

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
            name = r_data['suggestions'][0]['value']
        except:
            logger.warn('Api returned invalid format: %s', response.text)
            raise _InvalidDadataFormat(response.text)
        return name


class _InvalidDadataFormat(Exception):
    def __init__(self, text: str):
        self.text = text


@app.cli.command()
def dadata():
    logger.debug('Start.')
    noname = Shop.name.in_(('unknown', '')) | Shop.name.is_(None)
    nofailed = FailedShopName.id.is_(None)
    queryset = Shop.query.outerjoin(Shop.failed_shop_name).filter(noname & nofailed)
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
                    except _InvalidDadataFormat as e:
                        next_shop.failed_shop_name = FailedShopName(json=e.text, shop_id=next_shop.id)
                    except:
                        logger.exception('get_name')
                        continue

                    db.session.commit()
        except:
            logger.exception('')

        time.sleep(app.config['DAEMON_SLEEP'])
