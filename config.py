
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "greenleaf.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Used to protect Flask sessions
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-this-before-deployment"
    )
