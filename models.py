# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Mixin for timestamp fields
class TimestampMixin(object):
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.id} {self.username}>"

class Item(db.Model, TimestampMixin):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(12), unique=True, nullable=True) # String allows leading zeros
    brand = db.Column(db.String(24))
    item_type = db.Column(db.String(16))
    size = db.Column(db.String(8))
    local_category = db.Column(db.String(64))

    def __repr__(self):
        return f"<Item {self.id} {self.sku}>"

class EbayItem(db.Model):
    __tablename__ = 'ebay_item'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    aspect_values = db.Column(MutableDict.as_mutable(JSON), default=dict)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    ebay_category_id = db.Column(db.Integer, nullable=True)
    ebay_item_id = db.Column(db.String(18), unique=True)
    status = db.Column(db.String(16), index=True)  # e.g. draft/listed/sold
    image_url = db.Column(db.String(255))
    listed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    item = db.relationship("Item", backref=db.backref("ebay_listing", uselist=False))

    def __repr__(self):
        return f"<EbayItem {self.id} {self.title}>"

class EbayCategory(db.Model):
    __tablename__ = 'ebay_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('ebay_category.id'), nullable=True)
    path = db.Column(db.String(512), nullable=True)

    def __repr__(self):
        return f"<EbayCategory {self.id} {self.name}>"

class CachedAspect(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)  
    aspect_data = db.Column(MutableDict.as_mutable(JSON), default=dict)

    def __repr__(self):
        return f"<CachedAspect {self.category_id}>"

class SeenSKU(db.Model):
    __tablename__ = 'seen_skus'
    sku = db.Column(db.String(12), primary_key=True) # String allows leading zeros
