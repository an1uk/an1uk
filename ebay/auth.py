# ebay\auth.py

import requests
from flask import current_app

enable_debug = True

def debug(*args):
    if enable_debug:
        print("[ebay_auth DEBUG]:", *args)

import time

_token_cache = {
    "token": None,
    "expires_at": 0  # unix timestamp
}

# Get a cached OAuth token, fetch a new one if expired or missing.
def get_oauth_token(client_id=None, client_secret=None, use_sandbox=None):
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        # Token is still valid (plus a 1 minute safety margin)
        return _token_cache["token"]

    # --- Fetch new token as before ---
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
    token = resp.json()['access_token']
    expires_in = resp.json().get('expires_in', 7200)  # eBay usually sends this

    # Cache the token and expiry
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + int(expires_in)
    debug("[DEBUG]: Got new OAuth token, expires in", expires_in, "seconds")
    return token

### Original function
# def get_oauth_token(client_id=None, client_secret=None, use_sandbox=None):
#     cfg = current_app.config
#     use_sandbox = cfg['USE_SANDBOX'] if use_sandbox is None else use_sandbox
#     client_id = client_id or cfg['CLIENT_ID']
#     client_secret = client_secret or cfg['CLIENT_SECRET']
#     env = "sandbox" if use_sandbox else "production"
#     base_url = "https://api.sandbox.ebay.com" if use_sandbox else "https://api.ebay.com"
#     oauth_url = f"{base_url}/identity/v1/oauth2/token"
#     resp = requests.post(
#         oauth_url,
#         headers={'Content-Type': 'application/x-www-form-urlencoded'},
#         data={'grant_type': 'client_credentials', 'scope': 'https://api.ebay.com/oauth/api_scope'},
#         auth=(client_id, client_secret)
#     )
#     resp.raise_for_status()
#     token = resp.json().get('access_token')
#     debug("Token:", token[:10] + '...')
#     return token
