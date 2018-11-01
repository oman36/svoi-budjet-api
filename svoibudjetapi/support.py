from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: object):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict() if callable(getattr(obj, 'to_dict')) else obj.to_dict
        return JSONEncoder.default(self, obj)
