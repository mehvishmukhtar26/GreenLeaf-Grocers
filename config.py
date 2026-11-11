
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URL = os.environ.get("DATABASE_URL")
DEMO_MODE = os.environ.get("DEMO_MODE") == "1"


class Config:

    if DATABASE_URL:
        # Use PostgreSQL if a DATABASE_URL is provided
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        ) if DATABASE_URL.startswith("postgres://") else DATABASE_URL

    elif DEMO_MODE:
        # Separate temporary database for the online demo
        SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/greenleaf_demo.db"

    else:
        # Keep using your original local database
        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///" + os.path.join(
                BASE_DIR, "instance", "greenleaf.db"
            )
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-this-before-deployment"
    )
