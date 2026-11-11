
import os

from datetime import date, timedelta

from flask import Flask, redirect, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required
)
from sqlalchemy import func

from config import Config
from models import db, User, Supplier, Product, Sale, SaleItem

from routes.auth import auth_bp
from routes.products import products_bp
from routes.sales import sales_bp
from routes.reports import reports_bp
from routes.alerts import alerts_bp


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


# Register application blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(alerts_bp)


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard_page"))

    return redirect(url_for("auth.login"))


@app.route("/dashboard/home")
@login_required
def dashboard_page():

    if current_user.role == "admin":

        # Count all products
        total_products = Product.query.count()

        # Count all sales bills
        total_sales = Sale.query.count()

        # Calculate today's revenue
        today_revenue = (
            db.session.query(
                func.coalesce(func.sum(Sale.total_amount), 0)
            )
            .filter(Sale.sale_date == date.today())
            .scalar()
        )

        # Prepare sales data for the last 7 days
        today = date.today()

        sales_labels = []
        sales_values = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)

            daily_revenue = (
                db.session.query(
                    func.coalesce(func.sum(Sale.total_amount), 0)
                )
                .filter(Sale.sale_date == day)
                .scalar()
            )

            sales_labels.append(day.strftime("%a"))
            sales_values.append(float(daily_revenue))

        # Calculate sales revenue by product category
        category_sales = (
            db.session.query(
                Product.category,
                func.sum(SaleItem.quantity * SaleItem.price)
            )
            .join(
                SaleItem,
                Product.product_id == SaleItem.product_id
            )
            .group_by(Product.category)
            .all()
        )

        category_labels = [row[0] for row in category_sales]
        category_values = [float(row[1]) for row in category_sales]

        # Find the top 10 selling products
        
        top_products = (
    db.session.query(
        Product.name,
        func.sum(SaleItem.quantity).label("total_quantity")
    )
    .join(
        SaleItem,
        Product.product_id == SaleItem.product_id
    )
    .group_by(Product.product_id, Product.name)
    .order_by(func.sum(SaleItem.quantity).desc())
    .limit(10)
    .all()
)
        # Count products that need restocking
        low_stock_count = Product.query.filter(
            Product.stock_qty <= Product.reorder_level
        ).count()

        # Display admin dashboard
        return render_template(
            "dashboard.html",
            total_products=total_products,
            total_sales=total_sales,
            today_revenue=round(float(today_revenue), 2),
            low_stock_count=low_stock_count,
            sales_labels=sales_labels,
            sales_values=sales_values,
            category_labels=category_labels,
            category_values=category_values,
            top_products=top_products
        )

    # Display cashier dashboard
    return render_template("dashboard.html")


if __name__ == "__main__":

    print("GreenLeaf Grocers is starting...")
    print("Main Application: http://127.0.0.1:5000/")
    print("Login Page: http://127.0.0.1:5000/login")
    print("Products Page: http://127.0.0.1:5000/products")
    print("Billing Page: http://127.0.0.1:5000/billing")
    print("Receipt Page: http://127.0.0.1:5000/billing/receipt/553")
    print("Reports Page: http://127.0.0.1:5000/reports")
    print("Alerts Page: http://127.0.0.1:5000/alerts")

    app.run(debug=True)
