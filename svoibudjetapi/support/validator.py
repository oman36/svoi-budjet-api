import datetime
from svoibudjetapi.models import db


def is_valid_column_val(value, column):
    c_type = column.type
    if value is None and column.nullable:
        return True

    if isinstance(c_type, (db.String, db.Text, db.Numeric,)):
        return isinstance(value, str)

    elif isinstance(c_type, (db.Integer, db.BigInteger, db.SmallInteger,)):
        return not isinstance(value, bool) and isinstance(value, int)

    elif isinstance(c_type, (db.Float,)):
        return isinstance(value, float)

    elif isinstance(c_type, (db.Boolean,)):
        return isinstance(value, bool)

    elif isinstance(c_type, (db.DateTime,)):
        if isinstance(value, int):
            return True

        if not isinstance(value, str):
            return False
        try:
            datetime.datetime.strptime(value.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return False
        return True

    elif isinstance(c_type, (db.Date,)):
        if not isinstance(value, str):
            return False
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return False
        return True

    elif isinstance(c_type, (db.Time,)):
        if not isinstance(value, str):
            return False
        try:
            datetime.datetime.strptime(value, '%H:%M:%S')
        except ValueError:
            return False
        return True

    return True


def is_valid_model_dict(dict_, model_class):
    columns = {c.key: c for c in model_class.__table__.columns}
    for fields_name, field_value in dict_.items():
        if fields_name not in columns:
            raise ModelDoesNotHaveFieldException(model_class.__tablename__, fields_name, list(columns.keys()))
        if not is_valid_column_val(field_value, columns[fields_name]):
            raise InvalidFieldValueException(model_class.__tablename__, fields_name, field_value)


class ValidatorBaseException(BaseException):
    pass


class ModelDoesNotHaveFieldException(ValidatorBaseException):
    def __init__(self, class_name: str, field_name: str, exists: list):
        self.class_name = class_name
        self.field_name = field_name
        self.exists = exists

    def __str__(self):
        return (f'{self.class_name} does not have field {self.field_name}. Available: '
                + ', '.join(self.exists))


class InvalidFieldValueException(ValidatorBaseException):
    def __init__(self, class_name: str, field_name: str, value):
        self.class_name = class_name
        self.field_name = field_name
        self.value = value

    def __str__(self):
        return f'{repr(self.value)} invalid value for {self.class_name}.{self.field_name}'
