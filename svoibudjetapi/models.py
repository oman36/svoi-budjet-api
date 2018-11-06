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

        # hack for loading data
        if self._sa_instance_state.expired:
            getattr(self, next(self._sa_instance_state.expired_attributes.__iter__()))

        return {k: self.__serialize(v) for k, v in vars(self).items() if '_' != k[:1]}


class Timestamps:
    def __init__(self, *args, **kwargs):
        pass
    created_at = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)


class Shop(Model, Timestamps):
    __tablename__ = 'shops'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    inn = db.Column(db.BigInteger, unique=True)

    products = db.relationship('Product', back_populates='shop')
    checks = db.relationship('Check', back_populates='shop')

    def __repr__(self):
        return f'<Shop(name="{self.name}",inn={self.inn})>'


class Category(Model, Timestamps):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f'<Category(name="{self.name}")>'


class Product(Model, Timestamps):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('name', 'shop_id'),
    )

    shop = db.relationship('Shop', back_populates='products')
    items = db.relationship('Item', back_populates='product')

    def __repr__(self):
        return f'<Product(name="{self.name}", shop_id={self.shop_id})>'


class Check(Model, Timestamps):
    __tablename__ = 'checks'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, unique=True, nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    discount_sum = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    total_sum = db.Column(db.Numeric(10, 2), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id', ondelete='CASCADE'), nullable=False)

    shop = db.relationship('Shop', back_populates='checks')
    items = db.relationship('Item', back_populates='check')
    qr_string = db.relationship('QRString', back_populates='check')

    def __repr__(self):
        return f'<Check(shop_id={self.shop_id}, date="{self.date}")>'


class Item(Model, Timestamps):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Numeric(12, 4), nullable=False)
    sum = db.Column(db.Numeric(10, 2), nullable=False)

    check = db.relationship('Check', back_populates='items')
    product = db.relationship('Product', back_populates='items')

    def __repr__(self):
        return f'<Item(check_id={self.check_id}, product_id={self.product_id})>'


class QRString(Model, Timestamps):
    __tablename__ = 'qr_strings'

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.id', ondelete='SET NULL'), nullable=True)
    qr_string = db.Column(db.String(255), unique=True, nullable=False)
    is_valid = db.Column(db.Boolean, nullable=True)

    check = db.relationship('Check', back_populates='qr_string')

    def __repr__(self):
        return f'<QRString(qr_string="{self.qr_string}")>'
