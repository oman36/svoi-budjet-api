class IncludesAttachService:
    def __init__(self, includes: str):
        self.original_includes = includes
        self.parsed_includes = None

    def attach_includes(self, serialized: dict, model: object):
        for include_set in self.get_parsed_includes():
            self.load_includes(serialized, model, include_set[:])

    def load_includes(self, target: dict, model, includes: list):
        include = includes.pop(0)

        if not hasattr(model, include):
            return

        relation = getattr(model, include)

        if isinstance(relation, list):
            target[relation] = []
            for rel in relation:
                new = rel.serialized_()
                if len(includes):
                    self.load_includes(new, rel, includes)
                target[relation].append(new)
            return

        target[include] = relation.serialized_()

        if len(includes):
            self.load_includes(target[include], relation, includes)

    def get_parsed_includes(self):
        if self.parsed_includes is None:
            self.parsed_includes = []
            for relation in self.original_includes.split(','):
                include_set = [model for model in relation.split('.') if model]
                if include_set:
                    self.parsed_includes.append(include_set)

        return self.parsed_includes
