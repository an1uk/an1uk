# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'supersecret')
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@"
        f"{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # eBay credentials and environment
    EBAY_ENV = os.environ.get("EBAY_ENV", "sandbox").lower()
    EBAY_MARKETPLACE = os.environ.get('EBAY_MARKETPLACE', 'EBAY_GB')
    EBAY_ROOT_CATEGORY_ID = int(os.environ.get('EBAY_ROOT_CATEGORY_ID', '0'))

    SANDBOX_CLIENT_ID = os.environ.get("SANDBOX_CLIENT_ID")
    SANDBOX_CLIENT_SECRET = os.environ.get("SANDBOX_CLIENT_SECRET")
    PROD_CLIENT_ID = os.environ.get("PROD_CLIENT_ID")
    PROD_CLIENT_SECRET = os.environ.get("PROD_CLIENT_SECRET")

    USE_SANDBOX = EBAY_ENV == "sandbox"
    CLIENT_ID = SANDBOX_CLIENT_ID if USE_SANDBOX else PROD_CLIENT_ID
    CLIENT_SECRET = SANDBOX_CLIENT_SECRET if USE_SANDBOX else PROD_CLIENT_SECRET
    CATEGORY_TREE_ID = 0 if USE_SANDBOX else 3
    BASE_URL = "https://api.sandbox.ebay.com" if USE_SANDBOX else "https://api.ebay.com"

    # AWS S3
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_PREFIX = os.environ.get('S3_PREFIX')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-2')

    # CloudFront
    CF_IMAGE_BASE_URL = os.environ.get('CF_IMAGE_BASE_URL')

    # Misc
    CATEGORY_CACHE_FILE = os.environ.get('CATEGORY_CACHE_FILE', 'categories.json')
