
import os

from werkzeug.security import generate_password_hash

from app import app
from models import db, User
from seed_data import seed_database


with app.app_context():

    # Create database tables
    db.create_all()

    # Get demo admin details from environment variables
    username = os.environ.get("DEMO_ADMIN_USERNAME")
    password = os.environ.get("DEMO_ADMIN_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Demo admin username and password are required."
        )

    # Create admin account if it does not already exist
    existing_user = User.query.filter_by(
        username=username
    ).first()

    if not existing_user:

        admin = User(
            username=username,
            password_hash=generate_password_hash(password),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Demo admin account created.")

    else:
        print("Demo admin account already exists.")

    # Generate sample suppliers, products and sales
    seed_database()

    print("Online demo database is ready.")
