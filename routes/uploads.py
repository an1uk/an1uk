# routes\uploads.py
import os
from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required
from an1uk.models import db, Item
from .utils import list_s3_keys, extract_sku_from_key

uploads = Blueprint('uploads', __name__)

BUCKET_NAME = os.getenv('S3_BUCKET', 'an1uk2')
PREFIX = os.getenv('S3_PREFIX', 'items/')

@uploads.route('/check-uploads')
@login_required
def check_uploads():
    keys = list_s3_keys(BUCKET_NAME, PREFIX)
    found = {extract_sku_from_key(k) for k in keys if extract_sku_from_key(k)}
    existing_items = {i.sku for i in Item.query.filter(Item.sku.in_(found)).all()}
    new_skus = found - existing_items
    # Add new Item rows for new SKUs
    db.session.add_all([Item(sku=sku) for sku in new_skus])
    db.session.commit()
    flash(f"Found {len(new_skus)} new Items. Total in S3: {len(found)}.", 'info')
    return redirect(url_for('main.index'))
