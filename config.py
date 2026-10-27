
import os

# Find the main project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Store the SQLite database inside the instance folder
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "greenleaf.db")
    )

    # Track database changes through SQLAlchemy events
    SQLALCHEMY_TRACK_MODIFICATIONS = False
