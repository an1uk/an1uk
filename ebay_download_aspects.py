import requests
import json
from config import BASE_URL, CATEGORY_TREE_ID
from ebay_auth import get_oauth_token 

CATEGORY_ID = '185076'  # Example: Men's Shirts

OAUTH_URL = f"{BASE_URL}/identity/v1/oauth2/token"
ASPECTS_URL = (
    f"{BASE_URL}/commerce/taxonomy/v1/category_tree/{CATEGORY_TREE_ID}/"
    f"get_item_aspects_for_category?category_id={CATEGORY_ID}"
)

def fetch_aspects(category_id, access_token):
    url = f"{BASE_URL}/commerce/taxonomy/v1/category_tree/{CATEGORY_TREE_ID}/get_item_aspects_for_category?category_id={category_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

if __name__ == '__main__':
    token = get_oauth_token()
    data = fetch_aspects(CATEGORY_ID, token)
    # Print or save aspects for inspection
    print(json.dumps(data, indent=2))
    with open('aspects_downloaded.json', 'w') as f:
        json.dump(data, f, indent=2)