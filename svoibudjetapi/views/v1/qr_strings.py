from flask import (
    jsonify,
    request,
    abort,
)

from svoibudjetapi import app
from svoibudjetapi.models import QRString
from svoibudjetapi.support import generate_joins, get_eval_sort_by_rule


@app.route('/v1/qr_strings', methods=['GET'])
def get_qr_strings():
    queryset = QRString.query.options(*generate_joins(request.args.get('include', ''), QRString))
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 10, int)

    bool_filters = {
        'is_valid': lambda v: QRString.is_valid == v,
        'with_check': lambda v: getattr(QRString.check_id, 'isnot' if v else 'is_')(None),
    }
    for key, callback in bool_filters.items():
        if key in request.args:
            try:
                is_valid = {'1': True, '0': False}[request.args[key]]
            except KeyError:
                return jsonify({
                    'message': f'Invalid value for "{key}". Must be 1 or 0.'
                }), 400

            queryset = queryset.filter(callback(is_valid))

    if 'sort_by' in request.args:
        try:
            sort_by_rule = get_eval_sort_by_rule(request.args['sort_by'], QRString)
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


@app.route('/v1/qr_strings/<int:id_>', methods=['GET'])
def get_qr_string(id_: int):
    queryset = QRString.query.options(*generate_joins(request.args.get('include', ''), QRString))
    check = queryset.get(id_)
    if check is None:
        return abort(404)

    return jsonify(check)
