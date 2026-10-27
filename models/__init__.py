
from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint


# Shared database object used by the application
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'cashier')",
            name="check_user_role"
        ),
    )


class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_qty = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    expiry_date = db.Column(db.Date, nullable=True)

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.supplier_id"),
        nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "unit_price >= 0",
            name="check_product_price"
        ),
        CheckConstraint(
            "stock_qty >= 0",
            name="check_product_stock"
        ),
        CheckConstraint(
            "reorder_level >= 0",
            name="check_reorder_level"
        ),
    )


class Sale(db.Model):
    __tablename__ = "sales"

    sale_id = db.Column(db.Integer, primary_key=True)
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    sale_time = db.Column(
        db.Time,
        nullable=False,
        default=lambda: datetime.now().time().replace(microsecond=0)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_sale_total"
        ),
    )


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    sale_item_id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.sale_id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.product_id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_sale_item_quantity"
        ),
        CheckConstraint(
            "price >= 0",
            name="check_sale_item_price"
        ),
    )
