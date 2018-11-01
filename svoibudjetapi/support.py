from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: object):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict() if callable(getattr(obj, 'to_dict')) else obj.to_dict
        return JSONEncoder.default(self, obj)


class IncludesLoader:
    def __init__(self, includes: str):
        self.original_includes = includes
        self.parsed_includes = None

    def load_includes(self, model: object) -> None:
        for include_set in self.get_parsed_includes():
            self.load_include(model, include_set)

    def load_include(self, model, includes: tuple, deep=0) -> None:
        include = includes[deep]

        if not hasattr(model, include):
            return

        relation = getattr(model, include)

        if len(includes) > deep + 1:
            if not isinstance(relation, list):
                relation = [relation]

            for rel in relation:
                self.load_include(rel, includes, deep + 1)

    def get_parsed_includes(self) -> [tuple]:
        if self.parsed_includes is None:
            self.parsed_includes = []
            for relation in self.original_includes.split(','):
                include_set = tuple(model for model in relation.split('.') if model)
                if include_set:
                    self.parsed_includes.append(include_set)

        return self.parsed_includes
