import datetime
import hashlib
import json
import os
import re

from svoibudjetapi import app, db
from svoibudjetapi.models import Check, Shop, Item, Product


def save_check_json(json_string: str):
    json_files_path = app.config['JSON_FILES_DIR']
    filename = hashlib.md5(json_string).hexdigets() + '.json'

    if not os.path.isdir(json_files_path):
        os.makedirs(json_files_path)

    with open(os.path.join(json_files_path, filename), 'w+') as file:
        file.write(json_string)


def save_check_from_json(json_string: str):
    data = json.loads(json_string)

    if isinstance(data['dateTime'], int) or re.match('^\d+$', data['dateTime']):
        date = datetime.datetime.fromtimestamp(data['dateTime']).isoformat()
    else:
        date = data['dateTime']

    check = Check.objects.filter(Check.date == date).first()

    if Check.objects.filter(date=date).first():
        return check

    shop = Shop.objects.filter(Shop.inn == data['userInn']).first()

    if shop is None:
        shop = Shop(inn=data['userInn'], name=data.get('user', 'unknown'))

    check = Check(
        date=date,
        total_sum=data['totalSum'] / 100,
        discount=data.get('discount', 0) or 0 / 100,
        discount_sum=data.get('discountSum', 0) or 0 / 100,
        shop=shop,
    )

    for item in data['items']:
        save_item(check, item)

    db.session.commit()

    return check


def save_item(check, item_data):
    item_data['name'] = item_data.get('name')

    if item_data['name'] is None:
        item_data['name'] = 'unknown_%d' % (
            Product.objects.filter(Product.shop == check.shop).count() + 1
        )
        product = None
    else:
        product = Product.objects.filter(name=item_data['name'], shop=check.shop).first()

    if product is None:
        product = Product(shop=check.shop, name=item_data['name'])

    item = Item(
        check_model=check,
        product=product,
        price=item_data['price'] / 100,
        quantity=item_data['quantity'],
        sum=item_data['sum'] / 100,
    )

    return item
