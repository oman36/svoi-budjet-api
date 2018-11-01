import datetime
import decimal
from svoibudjetapi import db


class Model(db.Model):
    __abstract__ = True

    def __serialize(self, val):
        if isinstance(val, (list, set, tuple)):
            return type(val)(self.__serialize(v) for v in val)

        elif isinstance(val, dict):
            return {k: self.__serialize(v) for k, v in val.items()}

        elif isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
            return str(val)

        elif isinstance(val, decimal.Decimal):
            return float(val)

        return val

    def to_dict(self):
        return {k: self.__serialize(v) for k, v in vars(self).items() if '_' != k[:1]}


class Shop(Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    inn = db.Column(db.BigInteger, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Shop(name={self.name},inn={self.inn})>'


class Category(Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Category(name={self.name})>'


class Product(Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    __table_args__ = (
        db.UniqueConstraint('name', 'shop_id'),
    )

    def __repr__(self):
        return f'<Product(name={self.name}, shop_id={self.shop_id})>'


class Check(Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, unique=True)
    discount = db.Column(db.Numeric(10, 2), default=0)
    discount_sum = db.Column(db.Numeric(10, 2), default=0)
    total_sum = db.Column(db.Numeric(10, 2))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Check(shop_id={self.shop_id}, date={self.date})>'


class Item(Model):
    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey('check.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
    price = db.Column(db.Numeric(10, 2))
    quantity = db.Column(db.Numeric(12, 4))
    sum = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Item(check_id={self.check_id}, product_id={self.product_id})>'


class QRData(Model):
    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey('check.id', ondelete='SET NULL'), nullable=True)
    qr_string = db.Column(db.String(255), unique=True)
    is_valid = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<QRData(qr_string={self.qr_string})>'
