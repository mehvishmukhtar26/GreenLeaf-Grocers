
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db, Product, Sale, SaleItem


sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/billing")
@login_required
def billing():
    products = Product.query.filter(
        Product.stock_qty > 0
    ).order_by(Product.name).all()

    return render_template(
        "billing.html",
        products=products
    )


@sales_bp.route("/billing/create", methods=["POST"])
@login_required
def create_bill():

    try:
        product_ids = request.form.getlist("product_id")
        quantities = request.form.getlist("quantity")

        discount = Decimal(
            request.form.get("discount", "0")
        )

        # Validate discount
        if not discount.is_finite() or not Decimal("0") <= discount <= Decimal("100"):
            raise ValueError("Discount must be between 0 and 100.")

        if not product_ids or len(product_ids) != len(quantities):
            raise ValueError("Please select at least one product.")

        # Combine repeated products
        cart = {}

        for product_id, quantity in zip(product_ids, quantities):
            product_id = int(product_id)
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            cart[product_id] = cart.get(product_id, 0) + quantity

        # Fetch all products
        products = Product.query.filter(
            Product.product_id.in_(cart.keys())
        ).all()

        product_map = {
            product.product_id: product
            for product in products
        }

        if len(product_map) != len(cart):
            raise ValueError("One or more selected products do not exist.")

        subtotal = Decimal("0.00")

        for product_id, quantity in cart.items():
            product = product_map[product_id]

            if quantity > product.stock_qty:
                raise ValueError(
                    f"Insufficient stock for {product.name}. "
                    f"Available stock: {product.stock_qty}"
                )

            if product.expiry_date and product.expiry_date < date.today():
                raise ValueError(
                    f"{product.name} has expired and cannot be sold."
                )

            subtotal += Decimal(str(product.unit_price)) * quantity

        # Calculate discount and final amount
        discount_amount = (
            subtotal * discount / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total = (subtotal - discount_amount).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        # Create sale record
        sale = Sale(
            sale_date=date.today(),
            sale_time=datetime.now().time(),
            user_id=current_user.user_id,
            total_amount=total
        )

        db.session.add(sale)
        db.session.flush()

        # Save sale items and update stock
        for product_id, quantity in cart.items():
            product = product_map[product_id]

            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=product_id,
                quantity=quantity,
                price=product.unit_price
            )

            db.session.add(sale_item)

            product.stock_qty -= quantity

        db.session.commit()

        return redirect(
            url_for("sales.bill_receipt", sale_id=sale.sale_id)
        )

    except (ValueError, InvalidOperation):
        db.session.rollback()
        flash(
            "Invalid billing details. Check products, quantities and discount.",
            "error"
        )

    except Exception:
        db.session.rollback()
        flash(
            "Something went wrong. The bill was not saved.",
            "error"
        )

    return redirect(url_for("sales.billing"))

@sales_bp.route("/billing/receipt/<int:sale_id>")
@login_required
def bill_receipt(sale_id):

    sale = db.session.get(Sale, sale_id)

    if sale is None:
        flash("Bill not found.", "error")
        return redirect(url_for("sales.billing"))

    # Cashiers can only view their own bills
    if current_user.role != "admin" and sale.user_id != current_user.user_id:
        flash("You cannot access this bill.", "error")
        return redirect(url_for("sales.billing"))

    items = (
    db.session.query(SaleItem, Product)
    .join(Product, SaleItem.product_id == Product.product_id)
    .filter(SaleItem.sale_id == sale_id)
    .all()
)

    return render_template(
        "receipt.html",
        sale=sale,
        items=items
    )
