from flask import (
    jsonify,
    request,
    abort,
)

from svoibudjetapi import app
from svoibudjetapi.models import Check
from svoibudjetapi.support import IncludesLoader


@app.route('/v1/checks', methods=['GET'])
def get_checks():
    queryset = Check.query
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 10, int)

    data = {
        'total_count': queryset.count(),
        'items': [],
    }

    for check in queryset[offset:offset + limit]:
        IncludesLoader(request.args.get('include', '')).load_includes(check)
        data['items'].append(check)

    return jsonify(data)


@app.route('/v1/checks/<int:id_>', methods=['GET'])
def get_check(id_: int):
    check = Check.query.get(id_)
    if check is None:
        return abort(404)

    IncludesLoader(request.args.get('include', '')).load_includes(check)

    return jsonify(check)
