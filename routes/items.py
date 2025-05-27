# routes\items.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from sqlalchemy import func
from models import db, Item, EbayCategory, EbayItem
from ebay.auth import get_oauth_token
from ebay.aspects import get_cached_aspects
from model_form_builder import generate_flask_model_and_form
from routes.utils import s3  # Only import the client, not BUCKET_NAME

items = Blueprint('items', __name__)

@items.route('/enter', methods=['GET'])
@login_required
def enter_item_data():
    raw_counts = dict(
        db.session.query(EbayItem.ebay_category_id, func.count(EbayItem.id))
        .filter(EbayItem.ebay_category_id.isnot(None))
        .group_by(EbayItem.ebay_category_id)
        .all()
    )
    cats = db.session.query(EbayCategory).all()
    cat_map = {c.id: c for c in cats}
    entries = []
    for cid_str, cnt in raw_counts.items():
        cid = int(cid_str)
        if cid not in cat_map:
            continue
        path_parts = []
        current = cat_map[cid]
        while current:
            if current.name.lower() == 'root':
                break
            path_parts.append(current.name)
            current = cat_map.get(current.parent_id)
        full_path = ' -> '.join(reversed(path_parts))
        entries.append({'path': full_path, 'count': cnt, 'category_id': cid})
    entries.sort(key=lambda e: e['count'], reverse=True)
    return render_template('enter_item_data.html', entries=entries)

@items.route('/items/edit/<int:item_id>', methods=['GET', 'POST'], endpoint='edit_item_page')
@login_required
def edit_item_page(item_id):
    ebay_item = EbayItem.query.filter_by(item_id=item_id).first_or_404()
    sku = ebay_item.item.sku
    path = f"/items/{sku[:2]}/{sku[2:4]}/{sku[4:6]}/"
    cf_base = current_app.config.get('CF_IMAGE_BASE_URL')
    bucket_name = current_app.config.get('S3_BUCKET')
    images = []
    for i in range(1, 10):
        key = f"{path}{i}.jpg"
        if cf_base:
            thumb = f"{cf_base}{key}?width=120&height=120&fit=cover"
            full  = f"{cf_base}{key}"
        else:
            thumb = full = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600
            )
        images.append({'thumb_url': thumb, 'full_url': full})
    label_key = f"{path}label.jpg"
    if cf_base:
        images.append({
            'thumb_url': f"{cf_base}{label_key}?width=120&height=120&fit=cover",
            'full_url': f"{cf_base}{label_key}"
        })
    else:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': label_key},
            ExpiresIn=3600
        )
        images.append({'thumb_url': url, 'full_url': url})

    # Use current_app.config for config values
    access_token = get_oauth_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    category_id = ebay_item.ebay_category_id
    aspects = get_cached_aspects(category_id, headers)
    if not aspects:
        flash(f"No aspects found for category {category_id}", 'danger')
        return redirect(url_for('items.list_items_by_category', category_id=category_id))
    Model, Form, required_field_names, chip_fields, single_value_fields, select_fields, datalist_fields, initial_values, forced_default_chip, yesno_fields = generate_flask_model_and_form(category_id, aspects, db)
    form = Form(obj=ebay_item)
    for fname, initial in initial_values.items():
        if hasattr(form, fname):
            getattr(form, fname).data = ebay_item.aspect_values.get(fname, initial)
    if form.validate_on_submit():
        ebay_item.title = form.title.data
        ebay_item.price = form.price.data
        ebay_item.description = form.description.data
        ebay_item.aspect_values = {
            field.name: field.data for field in form
            if field.name not in ('csrf_token', 'submit', 'title', 'price', 'description')
        }
        db.session.commit()
        flash('Item updated successfully.', 'success')
        return redirect(url_for('items.list_items_by_category', category_id=ebay_item.ebay_category_id))
    return render_template('edit_item.html', ebay_item=ebay_item, images=images, form=form)

@items.route('/items/by-category/<int:category_id>')
@login_required
def list_items_by_category(category_id):
    category = EbayCategory.query.get_or_404(category_id)
    items_ = db.session.query(Item, EbayItem).join(
        EbayItem, Item.id == EbayItem.item_id
    ).filter(EbayItem.ebay_category_id == category_id).all()
    return render_template('list_items_sheet.html', items=items_, category=category)

@items.route('/api/items/by-category/<int:category_id>')
@login_required
def api_items_by_category(category_id):
    results = db.session.query(Item, EbayItem).join(
        EbayItem, Item.id == EbayItem.item_id
    ).filter(EbayItem.ebay_category_id == category_id).all()
    return jsonify([
        {
            'id': ebay_item.id,
            'item_id': item.id,
            'sku': item.sku,
            'title': ebay_item.title,
            'price': str(ebay_item.price),
            'description': ebay_item.description or ""
        } for item, ebay_item in results
    ])

@items.route('/api/items/bulk_update', methods=['POST'])
@login_required
def api_items_bulk_update():
    for row in request.json.get('items', []):
        item = Item.query.get(row['id'])
        if item:
            item.title = row.get('title', item.title)
            item.price = row.get('price', item.price)
            item.description = row.get('description', item.description)
    db.session.commit()
    return jsonify({'status': 'ok'})
