from functools import wraps
import os

from flask import (
    jsonify,
    request,
    abort,
    send_file,
)
from proverkacheka.api import API
from proverkacheka.exceptions import InvalidQueryStringException

from svoibudjetapi import (
    app,
    db,
)
from svoibudjetapi.models import QRString
from svoibudjetapi.support import (
    generate_joins,
    get_eval_sort_by_rule,
    validator,
    qr_string_images,
    http_errors_codes,
)


@wraps(app.route)
def route(rule, **options):
    return app.route('/api/v1/qr_strings' + rule, **options)


@route('', methods=['GET'])
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
                    'message': f'Invalid value for "{key}". Must be 1 or 0.',
                    'code': http_errors_codes.INVALID_BOOL_VAL,
                }), 400

            queryset = queryset.filter(callback(is_valid))

    if 'sort_by' in request.args:
        try:
            sort_by_rule = get_eval_sort_by_rule(request.args['sort_by'], QRString)
        except AttributeError:
            return jsonify({
                'message': f'Invalid value for sort_by. Must valid field name or field name with prefix -/+.',
                'code': http_errors_codes.INVALID_SORT_KEY,
            }), 400

        queryset = queryset.order_by(sort_by_rule)

    data = {
        'total_count': queryset.count(),
        'items': queryset[offset:offset + limit],
    }

    return jsonify(data)


@route('/<int:id_>', methods=['GET'])
def get_qr_string(id_: int):
    queryset = QRString.query.options(*generate_joins(request.args.get('include', ''), QRString))
    model = queryset.get(id_)
    if model is None:
        return abort(404)

    return jsonify(model)


@route('', methods=['POST'])
def post_qr_strings():
    try:
        post_json = request.get_json()
    except ValueError:
        return jsonify({
            'message': 'Invalid json format',
            'code': http_errors_codes.INVALID_JSON_FORMAT,
        }), 400

    qr_string = (post_json.get('qr_string', '') if isinstance(post_json, dict) else '').strip()

    if '' == qr_string:
        return jsonify({
            'message': 'qr_string is required.',
            'code': http_errors_codes.FIELDS_REQUIRED,
            'fields': ['qr_string'],
        }), 400

    try:
        API().is_valid_query_string(qr_string, silent=False)
    except InvalidQueryStringException as e:
        return jsonify({
            'message': str(e),
            'code': http_errors_codes.INVALID_QUERY_STRING,
        }), 400

    model = QRString.query.filter(QRString.qr_string == qr_string).first()
    if model is not None:
        return jsonify({
            'message': f'qr_string="{qr_string}" already exists',
            'code': http_errors_codes.ALREADY_EXISTS,
            'item': model
        }), 409

    model = QRString(qr_string=qr_string)
    db.session.add(model)
    db.session.commit()

    return jsonify(model), 201


@route('/<int:id_>', methods=['PATCH'])
def patch_qr_string(id_):
    model = QRString.query.get(id_)

    if model is None:
        abort(404)

    try:
        patch_json = request.get_json()
    except ValueError:
        return jsonify({
            'message': 'Invalid json format.',
            'code': http_errors_codes.INVALID_JSON_FORMAT,
        }), 400

    if not isinstance(patch_json, dict):
        return jsonify({
            'message': 'Json must be object.',
            'code': http_errors_codes.INVALID_JSON_FORMAT,
        }), 400

    patch_json = {k: v for k, v in patch_json.items() if k not in ('created_at', 'updated_at')}

    try:
        validator.is_valid_model_dict(patch_json, QRString)
    except validator.ValidatorBaseException as e:
        return jsonify({
            'message': str(e),
            'code': http_errors_codes.INVALID_MODEL_DATA,
        }), 400

    if 'qr_string' in patch_json:
        exist = QRString.query.filter(
            QRString.qr_string == patch_json['qr_string'],
            QRString.id != id_,
        ).first()
        if exist is not None:
            return jsonify({
                'message': f'qr_string="{patch_json["qr_string"]}" already exists.',
                'code': http_errors_codes.ALREADY_EXISTS,
                'item': exist,
            }), 409

    for field, value in patch_json.items():
        setattr(model, field, value)

    db.session.commit()

    return jsonify(model), 200


@route('/<int:id_>', methods=['DELETE'])
def delete_qr_string(id_):
    model = QRString.query.get(id_)

    if model is None:
        abort(404)

    db.session.delete(model)
    db.session.commit()

    return jsonify({}), 200


@route('/<int:id_>/images', methods=['GET'])
def get_qr_string_images(id_: int):
    queryset = QRString.query.options(*generate_joins(request.args.get('include', ''), QRString))
    model = queryset.get(id_)
    if model is None:
        return abort(404)

    result = {'items': []}
    for uri in qr_string_images.get_links(id_):
        result['items'].append({
            'link': f'{request.host_url}{uri}',
        })

    result['total_count'] = len(result['items'])
    return jsonify(result)


@route('/<int:id_>/images', methods=['DELETE'])
def delete_qr_string_images(id_: int):
    path = qr_string_images.get_path(id_)
    if not os.path.isdir(path):
        return abort(404)

    try:
        for file_name in qr_string_images.get_file_names(id_):
            os.unlink(qr_string_images.get_path(id_, file_name))
    except OSError:
        return jsonify({
            'message': 'Server error',
        }), 500

    return jsonify({})


@route('/<int:id_>/images', methods=['POST'])
def post_qr_string_image(id_: int):
    if len(request.files) == 0:
        return jsonify({
            'message': 'Files are required',
            'code': http_errors_codes.FIELDS_REQUIRED,
            'fields': ('file',)
        }), 400

    for file_storage in request.files.values():
        if file_storage.mimetype not in qr_string_images.VALID_MIME:
            return jsonify({
                'message': f'{file_storage.mimetype} is invalid MIME type.'
                           f' Allowed: {", ".join(qr_string_images.VALID_MIME)}',
                'code': http_errors_codes.INVALID_MIME,
                'valid': qr_string_images.VALID_MIME,
            }), 400

    target_dir = qr_string_images.get_path(id_)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    result = {'items': []}
    for name, file_storage in request.files.items():
        file_name = qr_string_images.generate_file_name(id_, file_storage)
        file_storage.save(qr_string_images.get_path(id_, file_name))
        result['items'].append({
            'name': name,
            'link': f'{request.host_url}{qr_string_images.get_link(id_, file_name)}',
        })

    return jsonify(result), 201


@route('/<int:id_>/images/<string:filename>', methods=['GET'])
def get_qr_string_image(id_: int, filename: str):
    path = qr_string_images.get_path(id_, filename)

    if not os.path.isfile(path):
        return abort(404)

    return send_file(path)


@route('/<int:id_>/images/<string:file_name>', methods=['DELETE'])
def delete_qr_string_image(id_: int, file_name: str):
    path = qr_string_images.get_path(id_, file_name)
    if not os.path.isfile(path):
        return abort(404)

    try:
        os.unlink(path)
    except OSError:
        return jsonify({
            'message': 'Server error',
        }), 500

    return jsonify({})
