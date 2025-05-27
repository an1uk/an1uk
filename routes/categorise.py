import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from sqlalchemy import text
from models import db, Item, EbayCategory, EbayItem, SeenSKU

categorise = Blueprint('categorise', __name__)

@categorise.route('/api/categories/<int:parent_id>')
@login_required
def get_subcategories(parent_id):
    children = EbayCategory.query.filter_by(parent_id=parent_id).order_by(EbayCategory.name).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in children])

@categorise.route('/categorise', methods=['GET', 'POST'])
@login_required
def categorise_items():
    if request.method == 'POST':
        ebay_cat = request.form['ebay_category_id']
        skus = request.form.getlist('sku')
        items = Item.query.filter(Item.sku.in_(skus)).all()
        id_map = {item.sku: item for item in items}
        count = 0
        for sku in skus:
            item = id_map.get(sku)
            if not item:
                continue
            ebay_item = EbayItem.query.filter_by(item_id=item.id).first()
            if ebay_item:
                ebay_item.ebay_category_id = ebay_cat
            else:
                db.session.add(EbayItem(item_id=item.id, title='Untitled', price=0, ebay_category_id=ebay_cat))
            count += 1
        db.session.commit()
        flash(f"Categorised {count} items.", 'success')
        return redirect(url_for('categorise.categorise_items'))
    tracked_ids = {e.item_id for e in EbayItem.query.filter(EbayItem.ebay_category_id.isnot(None)).all()}
    all_seen = [s.sku for s in SeenSKU.query.all()]
    sku_to_id = {item.sku: item.id for item in Item.query.filter(Item.sku.in_(all_seen)).all()}
    uncategorised = [sku for sku, iid in sku_to_id.items() if iid not in tracked_ids]
    cf = current_app.config.get('CF_IMAGE_BASE_URL')
    items = []
    for sku in sorted(uncategorised):
        key = f"items/{sku[:2]}/{sku[2:4]}/{sku[4:6]}/1.jpg"
        if cf:
            thumb = f"{cf}/{key}?width=120&height=120&fit=cover"
            full = f"{cf}/{key}"
        else:
            from .utils import s3, BUCKET_NAME  # For presigned url if needed
            thumb = full = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': key}, ExpiresIn=3600)
        items.append({'sku': sku, 'thumb_url': thumb, 'full_url': full})
    categories = db.session.execute(text('SELECT id, name FROM ebay_category ORDER BY name')).fetchall()
    return render_template('categorise.html', items=items, ebay_categories=categories, ebay_root=int(os.getenv('EBAY_ROOT_CATEGORY_ID', '0')))
