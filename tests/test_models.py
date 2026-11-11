
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from models import db, User, Supplier, Product, Sale, SaleItem


def test_product_can_be_saved(client):
    product = Product(
        name="Test Apple",
        category="Fruits",
        unit_price=Decimal("50.00"),
        stock_qty=20,
        reorder_level=5
    )

    db.session.add(product)
    db.session.commit()

    saved_product = Product.query.filter_by(
        name="Test Apple"
    ).first()

    assert saved_product is not None
    assert saved_product.stock_qty == 20


def test_supplier_can_be_saved(client):
    supplier = Supplier(
        name="Test Supplier",
        phone="1234567890",
        email="test@example.com"
    )

    db.session.add(supplier)
    db.session.commit()

    saved_supplier = Supplier.query.filter_by(
        name="Test Supplier"
    ).first()

    assert saved_supplier is not None


def test_sale_and_sale_item_can_be_saved(client):
    user = User(
        username="testadmin",
        password_hash="test-hash",
        role="admin"
    )

    product = Product(
        name="Test Banana",
        category="Fruits",
        unit_price=Decimal("25.00"),
        stock_qty=10,
        reorder_level=2
    )

    db.session.add_all([user, product])
    db.session.flush()

    sale = Sale(
        user_id=user.user_id,
        total_amount=Decimal("50.00")
    )

    db.session.add(sale)
    db.session.flush()

    item = SaleItem(
        sale_id=sale.sale_id,
        product_id=product.product_id,
        quantity=2,
        price=Decimal("25.00")
    )

    db.session.add(item)
    db.session.commit()

    assert Sale.query.count() == 1
    assert SaleItem.query.count() == 1


def test_product_rejects_negative_stock(client):
    product = Product(
        name="Invalid Product",
        category="Fruits",
        unit_price=Decimal("20.00"),
        stock_qty=-5,
        reorder_level=2
    )

    db.session.add(product)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()


def test_product_rejects_negative_price(client):
    product = Product(
        name="Invalid Price Product",
        category="Fruits",
        unit_price=Decimal("-10.00"),
        stock_qty=5,
        reorder_level=2
    )

    db.session.add(product)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()


def test_product_stock_can_be_updated(client):
    product = Product(
        name="Test Orange",
        category="Fruits",
        unit_price=Decimal("30.00"),
        stock_qty=20,
        reorder_level=5
    )

    db.session.add(product)
    db.session.commit()

    product.stock_qty = 15
    db.session.commit()

    updated_product = Product.query.filter_by(
        name="Test Orange"
    ).first()

    assert updated_product.stock_qty == 15


def test_low_stock_product_can_be_identified(client):
    product = Product(
        name="Low Stock Apple",
        category="Fruits",
        unit_price=Decimal("40.00"),
        stock_qty=3,
        reorder_level=10
    )

    db.session.add(product)
    db.session.commit()

    low_stock_products = Product.query.filter(
        Product.stock_qty <= Product.reorder_level
    ).all()

    assert len(low_stock_products) == 1
    assert low_stock_products[0].name == "Low Stock Apple"

