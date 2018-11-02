from flask import (
    jsonify,
    request,
    abort,
)

from svoibudjetapi import app
from svoibudjetapi.models import Check
from svoibudjetapi.support import generate_joins


@app.route('/v1/checks', methods=['GET'])
def get_checks():
    queryset = Check.query.options(*generate_joins(request.args.get('include', ''), Check))
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 10, int)

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