
from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import login_required

from models import Product

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/alerts")
@login_required
def alerts_page():

    today = date.today()
    next_30_days = today + timedelta(days=30)

    # Products with low stock
    low_stock = Product.query.filter(
        Product.stock_qty <= Product.reorder_level
    ).order_by(Product.stock_qty).all()

    # Products that have already expired
    expired_products = Product.query.filter(
        Product.expiry_date < today
    ).order_by(Product.expiry_date).all()

    # Products expiring within the next 30 days
    expiring_soon = Product.query.filter(
        Product.expiry_date >= today,
        Product.expiry_date <= next_30_days
    ).order_by(Product.expiry_date).all()

    return render_template(
        "alerts.html",
        low_stock=low_stock,
        expired_products=expired_products,
        expiring_soon=expiring_soon
    )
