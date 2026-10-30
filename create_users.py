
from getpass import getpass

from werkzeug.security import generate_password_hash

from app import app
from models import db, User


def create_account(username, role):
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        print(f"Username '{username}' already exists.")
        return

    password = getpass(f"Enter password for {username}: ")
    confirm_password = getpass("Confirm password: ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    print(f"{role.title()} account created successfully.")


with app.app_context():
    print("Create an account for GreenLeaf Grocers.")
    username = input("Enter username: ").strip()

    if not username:
        print("Username cannot be empty.")
    else:
        role = input("Enter role (admin/cashier): ").strip().lower()

        if role not in ("admin", "cashier"):
            print("Invalid role. Enter admin or cashier.")
        else:
            create_account(username, role)
