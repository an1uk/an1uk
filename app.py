from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecret')
app.config['CF_IMAGE_BASE_URL'] = os.getenv('CF_IMAGE_BASE_URL', '')
app.config['CATEGORY_CACHE_FILE'] = os.getenv('CATEGORY_CACHE_FILE', 'categories.json')

db.init_app(app)
Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.cli.command('refresh-categories')
def refresh_categories():
    """Reload the eBay category tree into the database."""
    from routes import cache_to_db
    count = cache_to_db(app)
    print(f"eBay categories refreshed. {count} cached.")

# Register blueprint from routes
from routes import register_blueprints
register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True)

from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    # your app config, db, login, etc.
    register_blueprints(app)
    return app
