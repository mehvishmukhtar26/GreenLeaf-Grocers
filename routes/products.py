import csv
import io

from datetime import date
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, Response
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

@products_bp.route("/products/export")
@login_required
def export_products():

    if current_user.role != "admin":
        flash("Only administrators can export products.", "error")
        return redirect("/products")

    products = Product.query.order_by(Product.product_id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV column headings
    writer.writerow([
        "name",
        "category",
        "unit_price",
        "stock_qty",
        "reorder_level",
        "expiry_date",
        "supplier_id"
    ])

    # Write each product
    for product in products:
        writer.writerow([
            product.name,
            product.category,
            product.unit_price,
            product.stock_qty,
            product.reorder_level,
            product.expiry_date or "",
            product.supplier_id or ""
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=greenleaf_products.csv"
        }
    )


@products_bp.route("/products/import", methods=["POST"])
@login_required
def import_products():

    if current_user.role != "admin":
        flash("Only administrators can import products.", "error")
        return redirect("/products")

    uploaded_file = request.files.get("file")

    if not uploaded_file or uploaded_file.filename == "":
        flash("Please select a CSV file.", "error")
        return redirect("/products")

    if not uploaded_file.filename.lower().endswith(".csv"):
        flash("Please upload a CSV file.", "error")
        return redirect("/products")

    try:
        content = uploaded_file.stream.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))

        required_columns = {
            "name", "category", "unit_price",
            "stock_qty", "reorder_level",
            "expiry_date", "supplier_id"
        }

        if not reader.fieldnames or not required_columns.issubset(
            set(reader.fieldnames)
        ):
            raise ValueError("CSV file has missing or incorrect column headings.")

        imported_count = 0

        for row in reader:
            name = (row.get("name") or "").strip()
            category = (row.get("category") or "").strip()

            if not name or not category:
                raise ValueError("Product name and category are required.")

            unit_price = float(row["unit_price"])
            stock_qty = int(row["stock_qty"])
            reorder_level = int(row["reorder_level"])

            if unit_price < 0 or stock_qty < 0 or reorder_level < 0:
                raise ValueError("Price and stock values cannot be negative.")

            expiry_text = (row.get("expiry_date") or "").strip()
            expiry_date = (
                date.fromisoformat(expiry_text)
                if expiry_text else None
            )

            supplier_text = (row.get("supplier_id") or "").strip()
            supplier_id = int(supplier_text) if supplier_text else None

            product = Product(
                name=name,
                category=category,
                unit_price=unit_price,
                stock_qty=stock_qty,
                reorder_level=reorder_level,
                expiry_date=expiry_date,
                supplier_id=supplier_id
            )

            db.session.add(product)
            imported_count += 1

        if imported_count == 0:
            raise ValueError("The CSV file contains no products.")

        db.session.commit()

        flash(
            f"{imported_count} products imported successfully.",
            "success"
        )

    except Exception as error:
        db.session.rollback()
        flash(f"Import failed: {error}", "error")

    return redirect("/products")

