# 3_update_ebay_categories.py
# Contains code for managing eBay categories, fetching and caching category data.

import os
import json
import time
import requests
from flask import current_app
from models import db, EbayCategory
from requests.exceptions import HTTPError
from ebay.auth import get_oauth_token

enable_debug = True

def debug(*args):
    if enable_debug:
        print("[category_utils DEBUG]:", *args)

# You can import this from category_utils_helpers if available
def flatten_category_tree(node, parent_id=None, path=None):
    if path is None:
        path = []

    cat_info = node.get('category', {})
    cat_id_str = cat_info.get('categoryId')
    cat_name = cat_info.get('categoryName')

    # If no valid categoryId or name, skip yielding this node
    if not cat_id_str or not cat_name:
        # still recurse into children under same parent/path
        for child in node.get('childCategoryTreeNodes', []):
            yield from flatten_category_tree(child, parent_id, path)
        return

    cat_id = int(cat_id_str)

    # Build full path
    current_path = path + [cat_name]
    full_path = ' > '.join(current_path)

    # Yield current node
    yield (cat_id, cat_name, parent_id, full_path)

    # Recurse into children
    for child in node.get('childCategoryTreeNodes', []):
        yield from flatten_category_tree(child, cat_id, current_path)

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

if __name__ == "__main__":
    from app import create_app  # Or 'from yourapp import app' if no factory
    app = create_app()
    with app.app_context():
        print("Updating eBay categories from eBay API...")
        count = cache_to_db(app)
        print(f"Successfully updated {count} categories in the database.")
