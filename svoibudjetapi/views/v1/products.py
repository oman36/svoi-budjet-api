from flask import (
    jsonify,
    request,
    abort,
)
from sqlalchemy import sql
from svoibudjetapi import (
    app,
    db,
)
from svoibudjetapi.models import (
    Product,
    Item,
)
from svoibudjetapi.support import (
    generate_joins,
    get_sort_by_rule,
    get_eval_sort_by_rule,
)


@app.route('/v1/products', methods=['GET'])
def get_products():
    queryset = Product.query.options(*generate_joins(request.args.get('include', ''), Product))
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 10, int)

    if 'sort_by' in request.args:
        field, direction = get_sort_by_rule(request.args['sort_by'])
        if field == 'min_price':
            min_price_subquery = db.session\
                .query(Item.product_id, sql.label('min_price', db.func.min(Item.price)))\
                .group_by(Item.product_id)\
                .subquery()

            queryset = queryset.join(min_price_subquery)\
                .order_by(min_price_subquery.c.min_price)\
                .with_entities(Product, min_price_subquery)
        else:
            try:
                sort_by_rule = getattr(getattr(Product, field), direction)()
            except AttributeError:
                return jsonify({
                    'message': f'Invalid value for sort_by. Must valid field name or field name with prefix -/+.'
                }), 400

            queryset = queryset.order_by(sort_by_rule)

    if 'name_contains' in request.args:
        queryset = queryset.filter(Product.name.contains(request.args['name_contains'].strip()))

    def transformer(item):
        if isinstance(item, tuple):
            item, item_id, min_price = item
            item = item.to_dict()
            item['min_price'] = float(min_price)
        return item

    data = {
        'total_count': queryset.count(),
        'items': [transformer(i) for i in queryset[offset:offset + limit]],
    }
    return jsonify(data)


@app.route('/v1/products/<int:id_>/items', methods=['GET'])
def get_product_items(id_):
    if Product.query.filter_by(id=id_).count() == 0:
        return abort(404)

    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 100, int)

    queryset = Item.query.filter_by(product_id=id_)\
        .options(*generate_joins(request.args.get('include', ''), Item))

    if 'sort_by' in request.args:
        try:
            sort_by_rule = get_eval_sort_by_rule(request.args['sort_by'], Item)
        except AttributeError:
            return jsonify({
                'message': f'Invalid value for sort_by. Must valid field name or field name with prefix -/+.'
            }), 400

        queryset = queryset.order_by(sort_by_rule)

    return jsonify({
        'total_count': queryset.count(),
        'items': queryset[offset:limit + offset],
    })