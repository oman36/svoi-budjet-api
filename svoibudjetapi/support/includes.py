from flask_sqlalchemy import orm


def parse_includes(original_includes: str) -> [[str]]:
    """Generates split relation names

    Original string is exploded by comma to groups.
    Each group is exploded by dot to relations.
    Each group is chain of relations.

    :param original_includes: string like 'shop,items.product.shop'
    :return: yields tuples of strings like ('shop'), ('items', 'product', 'shop')
    """
    for relation in original_includes.split(','):
        include_set_ = tuple(model_ for model_ in relation.split('.') if model_)
        if include_set_:
            yield include_set_


def generate_join(root_model: object, includes: [str]):
    """Tries to implement "load"(orm.joinedload or orm.subqueryload)

    Tries to implement "load" from chain of relations gotten from function `parse_includes`.
    "Loads" can be used for queryset.options(*loads).

    :param root_model: instance of flask_sqlalchemy.SQLAlchemy.Model
    :param includes: sequence of strings
    :return: None or "load"
    """
    loads = None
    current_model = root_model

    for include in includes:
        if not hasattr(current_model, include):
            break

        relation = getattr(current_model, include)
        current_model = relation.property.mapper.class_manager.class_
        if loads is None:
            loads = orm.joinedload(relation)
        else:
            loads = loads.subqueryload(relation)

    return loads


def generate_joins(string: str, model: object):
    """Generate rules for additional joins

    :param string: string that will be parsed by function `parse_includes`
    :param model: instance of flask_sqlalchemy.SQLAlchemy.Model. It is root model for relationships
    :return: generator of orm.joinedload or orm.subqueryload
    """

    for include_set in parse_includes(string):
        join = generate_join(model, include_set)
        if join:
            yield join
