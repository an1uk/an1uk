# Contains code for managing eBay categories, fetching and caching category data, and aspects.

import requests
from flask import current_app
from models import db, CachedAspect

enable_debug = True

def debug(*args):
    if enable_debug:
        print("[category_utils DEBUG]:", *args)

def fetch_aspects(category_id, headers):
    cfg = current_app.config
    url = f"{cfg['BASE_URL']}/commerce/taxonomy/v1/category_tree/{cfg['CATEGORY_TREE_ID']}/get_item_aspects_for_category?category_id={category_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        debug(f"Failed to fetch aspects for {category_id}: {resp.status_code} {resp.text}")
        return None
    return resp.json().get("aspects", [])

def get_cached_aspects(category_id, headers):
    cached = CachedAspect.query.get(category_id)
    if cached:
        return cached.aspect_data
    aspects = fetch_aspects(category_id, headers)
    if aspects:
        db.session.add(CachedAspect(category_id=category_id, data=aspects))
        db.session.commit()
    return aspects
