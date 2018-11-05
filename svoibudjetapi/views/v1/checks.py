from flask import (
    jsonify,
    request,
    abort,
)

from svoibudjetapi import app
from svoibudjetapi.models import Check, Item
from svoibudjetapi.support import generate_joins, get_eval_sort_by_rule


@app.route('/v1/checks', methods=['GET'])
def get_checks():
    queryset = Check.query.options(*generate_joins(request.args.get('include', ''), Check))
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 10, int)

    if 'sort_by' in request.args:
        try:
            sort_by_rule = get_eval_sort_by_rule(request.args['sort_by'], Check)
        except AttributeError:
            return jsonify({
                'message': f'Invalid value for sort_by. Must valid field name or field name with prefix -/+.'
            }), 400
        queryset = queryset.order_by(sort_by_rule)

    data = {
        'total_count': queryset.count(),
        'items': queryset[offset:offset + limit],
    }

    return jsonify(data)


@app.route('/v1/checks/<int:id_>', methods=['GET'])
def get_check(id_: int):
    queryset = Check.query.options(*generate_joins(request.args.get('include', ''), Check))
    check = queryset.get(id_)
    if check is None:
        return abort(404)

    return jsonify(check)


@app.route('/v1/checks/<int:id_>/items', methods=['GET'])
def get_check_items(id_: int):
    if Check.query.filter_by(id=id_).count() == 0:
        return abort(404)

    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 100, int)

    queryset = Item.query.filter_by(check_id=id_)\
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
