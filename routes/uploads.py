import os
from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required
from models import db, SeenSKU
from .utils import list_s3_keys, extract_sku_from_key

uploads = Blueprint('uploads', __name__)

BUCKET_NAME = os.getenv('S3_BUCKET', 'an1uk2')
PREFIX = os.getenv('S3_PREFIX', 'items/')

@uploads.route('/check-uploads')
@login_required
def check_uploads():
    keys = list_s3_keys(BUCKET_NAME, PREFIX)
    found = {extract_sku_from_key(k) for k in keys if extract_sku_from_key(k)}
    seen = {s.sku for s in SeenSKU.query.all()}
    new = found - seen
    db.session.add_all([SeenSKU(sku=sku) for sku in new])
    db.session.commit()
    flash(f"Found {len(new)} new SKUs. Total: {len(found)}.", 'info')
    return redirect(url_for('main.index'))
