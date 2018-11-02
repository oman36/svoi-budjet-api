from flask.json import JSONEncoder
from .includes import generate_joins, parse_includes, generate_join


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: object):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict() if callable(getattr(obj, 'to_dict')) else obj.to_dict
        return JSONEncoder.default(self, obj)


def get_sort_by_rule(string: str) -> (str, str):
    direction = 'asc'

    if string[:1] in ['-', '+']:
        if '-' == string[:1]:
            direction = 'desc'
        string = string[1:]

    return string, direction


def get_eval_sort_by_rule(string: str, model: object) -> (str, str):
    field, direction = get_sort_by_rule(string)
    return getattr(getattr(model, field), direction)()
