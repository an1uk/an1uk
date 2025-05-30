# standalone_scripts/reset_database.py
# WARNING: This will DROP and RECREATE all tables in your database!
# Intended for development/testing use only.

import sys
import os
# Add the project root (parent directory of this script) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from an1uk import create_app
from an1uk.models import db

# Import main from your admin script
from standalone_scripts.init_admin import main as create_admin

def main():
    app = create_app()
    with app.app_context():
        confirm = input(
            "WARNING: This will DROP and RECREATE all tables in your database! "
            "Are you sure? Type 'y' to proceed: "
        )
        if confirm.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        
        print("Dropping all tables...")
        db.drop_all()
        print("All tables dropped.")
        print("Recreating all tables...")
        db.create_all()
        print("All tables created (empty).")
        print("Database has been reset.")

        # Now create the admin user
        print("Creating admin user...")
        create_admin()  # This runs your admin creation logic

if __name__ == '__main__':
    main()
