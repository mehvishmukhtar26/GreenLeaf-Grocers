
from datetime import date

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from models import db, Sale, SaleItem, Product


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports_home():

    # Only admin can view reports
    if current_user.role != "admin":
        abort(403)

    today = date.today()

    # First day of the current month
    month_start = today.replace(day=1)

    # 1. Today's revenue
    daily_revenue = (
        db.session.query(db.func.coalesce(db.func.sum(Sale.total_amount), 0))
        .filter(Sale.sale_date == today)
        .scalar()
    )

    # Number of bills today
    daily_bills = Sale.query.filter_by(sale_date=today).count()

    # 2. This month's revenue
    monthly_revenue = (
        db.session.query(db.func.coalesce(db.func.sum(Sale.total_amount), 0))
        .filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= today
        )
        .scalar()
    )

    # 3. Top 10 selling products
    top_products = (
        db.session.query(
            Product.name,
            db.func.sum(SaleItem.quantity).label("total_quantity"),
            db.func.sum(
                SaleItem.price * SaleItem.quantity
            ).label("total_sales")
        )
        .join(SaleItem, Product.product_id == SaleItem.product_id)
        .group_by(Product.product_id, Product.name)
        .order_by(db.func.sum(SaleItem.quantity).desc())
        .limit(10)
        .all()
    )

    # 4. Category-wise sales
    category_sales = (
        db.session.query(
            Product.category,
            db.func.sum(SaleItem.quantity).label("total_quantity"),
            db.func.sum(
                SaleItem.price * SaleItem.quantity
            ).label("total_sales")
        )
        .join(SaleItem, Product.product_id == SaleItem.product_id)
        .group_by(Product.category)
        .order_by(db.func.sum(SaleItem.price * SaleItem.quantity).desc())
        .all()
    )

    # 5. Ten slow-moving products
    slow_products = (
        db.session.query(
            Product.name,
            Product.stock_qty,
            db.func.coalesce(
                db.func.sum(SaleItem.quantity), 0
            ).label("units_sold")
        )
        .outerjoin(
            SaleItem, Product.product_id == SaleItem.product_id
        )
        .group_by(Product.product_id, Product.name, Product.stock_qty)
        .order_by(db.func.coalesce(db.func.sum(SaleItem.quantity), 0).asc())
        .limit(10)
        .all()
    )

    return render_template(
        "reports.html",
        daily_revenue=daily_revenue,
        daily_bills=daily_bills,
        monthly_revenue=monthly_revenue,
        top_products=top_products,
        category_sales=category_sales,
        slow_products=slow_products
    )
