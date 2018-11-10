import datetime
import os
import time
import traceback
import json
import requests

from svoibudjetapi import app, db
from svoibudjetapi.models import Shop


@app.cli.command()
def dadata():
    def log_exception():
        if not os.path.isdir(app.config.get('LOG_DIR')):
            os.makedirs(app.config.get('LOG_DIR'))

        with open(os.path.join(app.config.get('LOG_DIR'), 'errors.log'), 'a+') as f:
            f.write('-' * 20 + datetime.datetime.now().strftime(' %Y-%m-%d %H:%M:%S ') + '-' * 20 + '\n')
            f.write(traceback.format_exc(20))

    def getName(inn):
        url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
        headers = {
            "Authorization": f"Token {app.config['DADATA_KEY']}",
            "Content-Type": "application/json",
        }
        data = {"query": inn, "count": 1}

        return requests.post(url, data=json.dumps(data), headers=headers)\
            .json()['suggestions'][0]['value']

    queryset = Shop.query.filter(Shop.name.in_(('unknown', '')))

    while True:
        try:
            step_size = 5
            offset = 0

            while True:
                next_shops = queryset[offset:offset + step_size]

                offset += step_size

                if len(next_shops) == 0:
                    break

                for next_shop in next_shops:  # type:Shop
                    try:
                        next_shop.name = getName(next_shop.inn)
                    except:
                        log_exception()
                        continue

                    db.session.commit()
        except:
            log_exception()

        time.sleep(5)
