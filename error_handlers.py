from flask import jsonify
from models import db

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({'error': 'Rate limit exceeded'}), 429