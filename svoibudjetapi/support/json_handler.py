import datetime
import json
import os
import re

from svoibudjetapi import app, db
from svoibudjetapi.models import Check, Shop, Item, Product


def save_check_json(json_string: str, qr_string_id: int):
    json_files_path = app.config['JSON_FILES_DIR']
    filename = f'{qr_string_id}.json'

    if not os.path.isdir(json_files_path):
        os.makedirs(json_files_path)

    with open(os.path.join(json_files_path, filename), 'w+') as file:
        file.write(json_string)


def save_check_from_json(json_string: str):
    data = json.loads(json_string)
    if 'document' in data:
        data = data['document']['receipt']

    if isinstance(data['dateTime'], int) or re.match('^\d+$', data['dateTime']):
        date = datetime.datetime.fromtimestamp(data['dateTime']).isoformat()
    else:
        date = data['dateTime']

    check = Check.query.filter(Check.date == date).first()

    if check is not None:
        return check

    shop = Shop.query.filter(Shop.inn == data['userInn']).first()

    if shop is None:
        shop = Shop(inn=data['userInn'], name=data.get('user', 'unknown'))

    check = Check(
        date=date,
        total_sum=data['totalSum'] / 100,
        discount=data.get('discount', 0) or 0 / 100,
        discount_sum=data.get('discountSum', 0) or 0 / 100,
        shop=shop,
    )

    save_items(check, data['items'])

    db.session.commit()

    return check


def save_items(check, items_data):
    unknown_count = None
    name2product = {}
    items = []
    for item_data in items_data:
        name = item_data.get('name')

        if not name:
            if unknown_count is None:
                unknown_count = Product.query.filter(Product.shop == check.shop).count()
            unknown_count += 1
            name = 'unknown_{}'.format(unknown_count)

        if name not in name2product:
            product = Product.query.filter(
                Product.name == name,
                Product.shop == check.shop,
            ).first()

            name2product[name] = product or Product(shop=check.shop, name=name)

        item = Item(
            check=check,
            product=name2product[name],
            price=item_data['price'] / 100,
            quantity=item_data['quantity'],
            sum=item_data['sum'] / 100,
        )

        items.append(item)
    return items
