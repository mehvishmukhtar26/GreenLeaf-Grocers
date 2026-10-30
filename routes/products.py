
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from flask_login import login_required, current_user

from models import db, Product, SaleItem


products_bp = Blueprint("products", __name__)


def admin_required():
    """Allow only administrators to manage products."""
    if current_user.role != "admin":
        flash("Only administrators can manage products.", "error")
        return False
    return True


@products_bp.route("/products")
@login_required
def product_list():
    if not admin_required():
        return redirect(url_for("dashboard_page"))

    search = request.args.get("search", "").strip()

    query = Product.query

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%")
            )
        )

    products = query.order_by(Product.name).all()

    return render_template(
        "products.html",
        products=products,
        search=search
    )


@products_bp.route("/products/add", methods=["POST"])
@login_required
def add_product():
    if not admin_required():
        return redirect(url_for("dashboard_page"))

    try:
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = Decimal(request.form.get("unit_price", ""))
        stock = int(request.form.get("stock_qty", ""))
        reorder = int(request.form.get("reorder_level", ""))
        expiry_text = request.form.get("expiry_date", "").strip()

        if not name or not category:
            raise ValueError("Name and category are required.")

        if not price.is_finite() or price < 0:
            raise ValueError("Price must be a valid non-negative amount.")

        if stock < 0 or reorder < 0:
            raise ValueError("Stock and reorder level cannot be negative.")

        expiry = date.fromisoformat(expiry_text) if expiry_text else None

        if Product.query.filter_by(name=name).first():
            raise ValueError("A product with this name already exists.")

        product = Product(
            name=name,
            category=category,
            unit_price=price,
            stock_qty=stock,
            reorder_level=reorder,
            expiry_date=expiry
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully.", "success")

    except (ValueError, InvalidOperation):
        db.session.rollback()
        flash("Invalid product details. Check every field.", "error")

    except Exception:
        db.session.rollback()
        flash("Could not save the product. Please try again.", "error")

    return redirect(url_for("products.product_list"))


@products_bp.route(
    "/products/<int:product_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_product(product_id):
    if not admin_required():
        return redirect(url_for("dashboard_page"))

    product = db.session.get(Product, product_id)

    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.product_list"))

    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            price = Decimal(request.form.get("unit_price", ""))
            stock = int(request.form.get("stock_qty", ""))
            reorder = int(request.form.get("reorder_level", ""))
            expiry_text = request.form.get("expiry_date", "").strip()

            if not name or not category:
                raise ValueError("Name and category are required.")

            if not price.is_finite() or price < 0:
                raise ValueError("Price must be non-negative.")

            if stock < 0 or reorder < 0:
                raise ValueError("Stock and reorder level cannot be negative.")

            expiry = date.fromisoformat(expiry_text) if expiry_text else None

            duplicate = Product.query.filter(
                Product.name == name,
                Product.product_id != product_id
            ).first()

            if duplicate:
                raise ValueError("Another product already has this name.")

            product.name = name
            product.category = category
            product.unit_price = price
            product.stock_qty = stock
            product.reorder_level = reorder
            product.expiry_date = expiry

            db.session.commit()
            flash("Product updated successfully.", "success")
            return redirect(url_for("products.product_list"))

        except (ValueError, InvalidOperation):
            db.session.rollback()
            flash("Invalid details. Please check the form.", "error")

        except Exception:
            db.session.rollback()
            flash("Could not update the product.", "error")

    return render_template("edit_product.html", product=product)


@products_bp.route(
    "/products/<int:product_id>/delete",
    methods=["POST"]
)
@login_required
def delete_product(product_id):
    if not admin_required():
        return redirect(url_for("dashboard_page"))

    product = db.session.get(Product, product_id)

    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.product_list"))

    # Preserve products referenced by past sales.
    if SaleItem.query.filter_by(product_id=product_id).first():
        flash(
            "This product has sales history and cannot be deleted.",
            "error"
        )
        return redirect(url_for("products.product_list"))

    try:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully.", "success")

    except Exception:
        db.session.rollback()
        flash("Could not delete the product.", "error")

    return redirect(url_for("products.product_list"))
