# standalone_scripts\init_admin.py
# Create an admin user for the application
# Would be nice to have this run automatically on first run

import os
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def main():
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'changeme')
    email = os.environ.get('ADMIN_EMAIL', f'{username}@example.com')

    if not password or password in ['changeme', '']:
        raise Exception("You must set ADMIN_PASSWORD environment variable to a secure password!")

    app = create_app()
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User {username} already exists.")
            return

        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, email=email, is_approved=True, is_admin=True)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created with email '{email}'.")

if __name__ == '__main__':
    main()
