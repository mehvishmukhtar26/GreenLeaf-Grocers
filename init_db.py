
from app import app
from models import db


# Work within the Flask application context
with app.app_context():
    # Create all tables that do not already exist
    db.create_all()

    print("GreenLeaf Grocers database created successfully!")

    print("\nTables created:")
    for table_name in db.metadata.tables:
        print(f"- {table_name}")

from app import app
from models import db


# Work within the Flask application context
with app.app_context():
    # Create all tables that do not already exist
    db.create_all()

    print("GreenLeaf Grocers database created successfully!")

    print("\nTables created:")
    for table_name in db.metadata.tables:
        print(f"- {table_name}")
