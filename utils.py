import os
import json
import time
import requests
from flask import current_app
from models import db, EbayCategory, CachedAspect
from category_utils_helpers import flatten_category_tree
from requests.exceptions import HTTPError

enable_debug = True

def debug(*args):
    if enable_debug:
        print("[category_utils DEBUG]:", *args)

def get_oauth_token(client_id=None, client_secret=None, use_sandbox=None):
    cfg = current_app.config
    use_sandbox = cfg['USE_SANDBOX'] if use_sandbox is None else use_sandbox
    client_id = client_id or cfg['CLIENT_ID']
    client_secret = client_secret or cfg['CLIENT_SECRET']
    env = "sandbox" if use_sandbox else "production"
    base_url = "https://api.sandbox.ebay.com" if use_sandbox else "https://api.ebay.com"
    oauth_url = f"{base_url}/identity/v1/oauth2/token"
    resp = requests.post(
        oauth_url,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={'grant_type': 'client_credentials', 'scope': 'https://api.ebay.com/oauth/api_scope'},
        auth=(client_id, client_secret)
    )
    resp.raise_for_status()
    token = resp.json().get('access_token')
    debug("Token:", token[:10] + '...')
    return token

def get_tree_id():
    cfg = current_app.config
    debug("Fetching default categoryTreeId for", cfg['EBAY_MARKETPLACE'])
    token = get_oauth_token()
    taxonomy_base = f"{cfg['BASE_URL']}/commerce/taxonomy/v1"
    url = f"{taxonomy_base}/get_default_category_tree_id?marketplace_id={cfg['EBAY_MARKETPLACE']}"
    resp = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    resp.raise_for_status()
    tree_id = resp.json().get('categoryTreeId')
    debug("Tree ID:", tree_id)
    return tree_id

def fetch_subtree(root_id=None):
    cfg = current_app.config
    token = get_oauth_token()
    tree_id = get_tree_id()
    if not tree_id:
        raise RuntimeError("Empty categoryTreeId")
    taxonomy_base = f"{cfg['BASE_URL']}/commerce/taxonomy/v1"
    ebay_root = cfg['EBAY_ROOT_CATEGORY_ID']
    if root_id is None:
        root = ebay_root
        debug("Defaulting to root", root)
        url = f"{taxonomy_base}/category_tree/{tree_id}/get_category_subtree?category_id={root}"
    elif root_id == 0:
        debug("Fetching full taxonomy tree")
        url = f"{taxonomy_base}/category_tree/{tree_id}"
    else:
        debug("Fetching subtree for root", root_id)
        url = f"{taxonomy_base}/category_tree/{tree_id}/get_category_subtree?category_id={root_id}"
    debug("GET URL:", url)
    resp = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    resp.raise_for_status()
    data = resp.json()
    node = (
        data.get('rootCategoryNode')
        or data.get('categorySubtreeNode')
        or data.get('categoryTreeNode')
        or {}
    )
    debug("Node keys:", list(node.keys()))
    return node

def download_and_cache(app=None):
    cfg = current_app.config
    cache_file = cfg.get('CATEGORY_CACHE_FILE', 'categories.json')
    ebay_root = cfg['EBAY_ROOT_CATEGORY_ID']
    debug("Cache file:", cache_file)
    use_cache = False
    if os.path.isfile(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        debug("Cache age:", age)
        tree = json.load(open(cache_file))
        if age < 86400 and tree:
            if ebay_root == 0 or tree.get('childCategoryTreeNodes'):
                debug("Using valid cache")
                return tree
        use_cache = True
    try:
        root_id = None if ebay_root != 0 else 0
        tree = fetch_subtree(root_id=root_id)
        json.dump(tree, open(cache_file, 'w'), indent=2)
        debug("Wrote cache, keys:", list(tree.keys()))
        return tree
    except HTTPError as e:
        debug("HTTPError", e.response.status_code, "use_cache?", use_cache)
        if use_cache:
            debug("Using stale cache")
            return json.load(open(cache_file))
        raise

def cache_to_db(app=None):
    ctx = app or current_app
    with ctx.app_context():
        tree = download_and_cache()
        count = 0
        for cid, name, parent, path in flatten_category_tree(tree):
            db.session.merge(
                EbayCategory(id=cid, name=name, parent_id=parent, path=path)
            )
            count += 1
        db.session.commit()
        debug("Merged count:", count)
        return count

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
        return cached.data
    aspects = fetch_aspects(category_id, headers)
    if aspects:
        db.session.add(CachedAspect(category_id=category_id, data=aspects))
        db.session.commit()
    return aspects
