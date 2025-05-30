from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config
from .models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # CLI command
    @app.cli.command('refresh-categories')
    def refresh_categories():
        from routes import cache_to_db
        count = cache_to_db(app)
        print(f"eBay categories refreshed. {count} cached.")

    from routes import register_blueprints
    register_blueprints(app)

    return app
