
import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user

from config import Config
from models import db, User, Supplier, Product, Sale, SaleItem
from routes.auth import auth_bp
from routes.products import products_bp


app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.instance_path, exist_ok=True)

# Connect the database to Flask
db.init_app(app)

# Set up login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# Register the login routes
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    return redirect(url_for("auth.login"))




from flask_login import login_required


@app.route("/dashboard/home")
@login_required
def dashboard_page():
    if current_user.role == "admin":
        return """
        <h1>Admin Dashboard</h1>
        <p>Manage products, stock, and reports.</p>
        <form action="/logout" method="post">
            <button type="submit">Logout</button>
        </form>
        """

    return """
    <h1>Cashier Dashboard</h1>
    <p>You can use the billing module here.</p>
    <form action="/logout" method="post">
        <button type="submit">Logout</button>
    </form>
    """


if __name__ == "__main__":
    app.run(debug=True)
