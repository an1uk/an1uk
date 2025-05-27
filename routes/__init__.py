# routes\__init__.py
from .auth import auth
from .main import main
from .uploads import uploads
from .categorise import categorise
from .items import items

def register_blueprints(app):
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(uploads)
    app.register_blueprint(categorise)
    app.register_blueprint(items)
