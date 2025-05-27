# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store the hashed password
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True) #
    sku = db.Column(db.String(12), unique=True, nullable=True) #
    brand = db.Column(db.String(24))
    item_type = db.Column(db.String(16))
    size = db.Column(db.String(8))
    local_category = db.Column(db.String(64))
    created = db.Column(db.DateTime, default=datetime.utcnow) #
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) #

class EbayItem(db.Model):
    __tablename__ = 'ebay_item'
    id = db.Column(db.Integer, primary_key=True) #
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False) #
    title = db.Column(db.String(80), nullable=False) #
    aspect_values = db.Column(MutableDict.as_mutable(JSON), default=dict) #
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    ebay_category_id = db.Column(db.Integer, nullable=True) #
    ebay_item_id = db.Column(db.String(18), unique=True) #
    status = db.Column(db.String(16), index=True)  # draft/listed/sold
    image_url = db.Column(db.String(255))
    listed_at = db.Column(db.DateTime) #
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow) #
    
    item = db.relationship("Item", backref=db.backref("ebay_listing", uselist=False))

class EbayCategory(db.Model):
    __tablename__ = 'ebay_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('ebay_category.id'), nullable=True)
    # Optionally, store path for UI convenience
    path = db.Column(db.String(512), nullable=True)

    def __repr__(self):
        return f"<Item {self.id} {self.name}>"

class CachedAspect(db.Model):
    category_id = db.Column(db.String, primary_key=True)
    data = db.Column(db.JSON, nullable=False)

class EbayAccountSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # optional if multi-account
    location = db.Column(db.String(128), nullable=False)
    postal_code = db.Column(db.String(16), nullable=False)
    shipping_profile_id = db.Column(db.String(32), nullable=False)
    return_profile_id = db.Column(db.String(32), nullable=False)
    payment_profile_id = db.Column(db.String(32), nullable=False)

# New SeenSKU Model
class SeenSKU(db.Model):
    __tablename__ = 'seen_skus'
    sku = db.Column(db.String(12), primary_key=True)
