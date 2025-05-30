# ebay\download_aspects.py

# import json
# from config import BASE_URL, CATEGORY_TREE_ID
# from ebay2.ebay.auth import get_oauth_token 

from flask import current_app
import requests
from datetime import datetime, timedelta
from ebay2.an1uk.models import db, CachedAspect

enable_debug = True

def debug(*args):
    if enable_debug:
        print("[DEBUG]:", *args)

def fetch_aspects(category_id, headers, force_refresh=False, max_age_hours=24):
    # Try to get from cache
    cached = CachedAspect.query.filter_by(category_id=category_id).first()

    # Determine if cache is fresh
    fresh = (
        cached and
        cached.updated_at and
        (datetime.utcnow() - cached.updated_at) < timedelta(hours=max_age_hours)
    )

    # Use cache unless forced to refresh or cache is missing/stale
    if cached and not force_refresh and fresh:
        debug(f"Returning cached aspects for {category_id}")
        return cached.aspect_data

    # Otherwise, fetch from eBay API
    cfg = current_app.config
    url = (
        f"{cfg['BASE_URL']}/commerce/taxonomy/v1/category_tree/"
        f"{cfg['CATEGORY_TREE_ID']}/get_item_aspects_for_category?category_id={category_id}"
    )
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        debug(f"Failed to fetch aspects for {category_id}: {resp.status_code} {resp.text}")
        # fallback to cache if available, even if stale
        if cached:
            debug(f"Returning STALE cached aspects for {category_id}")
            return cached.aspect_data
        return None

    aspects = resp.json().get("aspects", [])
    if cached:
        cached.aspect_data = aspects
        # cached.updated will auto-update on commit because of onupdate
    else:
        cached = CachedAspect(
            category_id=category_id,
            aspect_data=aspects
        )
        db.session.add(cached)
    db.session.commit()

    debug(f"Fetched and cached aspects for {category_id}")
    return aspects


#CATEGORY_ID = '185076'  # Example: Men's Shirts

#OAUTH_URL = f"{BASE_URL}/identity/v1/oauth2/token"
#ASPECTS_URL = (
#    f"{BASE_URL}/commerce/taxonomy/v1/category_tree/{CATEGORY_TREE_ID}/"
#    f"get_item_aspects_for_category?category_id={CATEGORY_ID}"
#)

#def fetch_aspects(category_id, access_token):
#    url = f"{BASE_URL}/commerce/taxonomy/v1/category_tree/{CATEGORY_TREE_ID}/get_item_aspects_for_category?category_id={category_id}"
#    headers = {'Authorization': f'Bearer {access_token}'}
#    resp = requests.get(url, headers=headers)
#    resp.raise_for_status()
#    return resp.json()

#if __name__ == '__main__':
#    token = get_oauth_token()
#    data = fetch_aspects(CATEGORY_ID, token)
    # Print or save aspects for inspection
#    print(json.dumps(data, indent=2))
#    with open('aspects_downloaded.json', 'w') as f:
#        json.dump(data, f, indent=2)

