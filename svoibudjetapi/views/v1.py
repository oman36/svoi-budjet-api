from flask import jsonify
from svoibudjetapi import app


@app.route('/v1/')
def hello_world():
    return jsonify({'message': 'Hello World!'})
