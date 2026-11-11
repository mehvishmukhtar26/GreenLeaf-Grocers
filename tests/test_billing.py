
from decimal import Decimal

from models import db, User, Product, Sale, SaleItem


def login_as_cashier(client):
    """Create a test cashier and log in."""
    user = User(
        username="billing_cashier",
        password_hash="test-hash",
        role="cashier"
    )

    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)
        session["_fresh"] = True

    return user


def create_test_product(stock=20):
    """Create a product for billing tests."""
    product = Product(
        name="Test Apple",
        category="Fruits",
        unit_price=Decimal("50.00"),
        stock_qty=stock,
        reorder_level=5
    )

    db.session.add(product)
    db.session.commit()

    return product


def test_successful_bill_is_created(client):
    login_as_cashier(client)
    product = create_test_product(stock=20)

    response = client.post(
        "/billing/create",
        data={
            "product_id": str(product.product_id),
            "quantity": "2",
            "discount": "0"
        }
    )

    assert response.status_code == 302
    assert "/billing/receipt/" in response.headers["Location"]
    assert Sale.query.count() == 1
    assert SaleItem.query.count() == 1

    sale = Sale.query.first()
    assert sale.total_amount == Decimal("100.00")


def test_stock_is_deducted_after_billing(client):
    login_as_cashier(client)
    product = create_test_product(stock=20)

    client.post(
        "/billing/create",
        data={
            "product_id": str(product.product_id),
            "quantity": "3",
            "discount": "0"
        }
    )

    updated_product = db.session.get(Product, product.product_id)

    assert updated_product.stock_qty == 17


def test_insufficient_stock_prevents_billing(client):
    login_as_cashier(client)
    product = create_test_product(stock=5)

    response = client.post(
        "/billing/create",
        data={
            "product_id": str(product.product_id),
            "quantity": "10",
            "discount": "0"
        }
    )

    assert response.status_code == 302
    assert Sale.query.count() == 0
    assert SaleItem.query.count() == 0

    unchanged_product = db.session.get(Product, product.product_id)
    assert unchanged_product.stock_qty == 5


def test_discount_is_calculated_correctly(client):
    login_as_cashier(client)
    product = create_test_product(stock=20)

    client.post(
        "/billing/create",
        data={
            "product_id": str(product.product_id),
            "quantity": "2",
            "discount": "10"
        }
    )

    sale = Sale.query.first()

    # 2 x 50 = 100; 10% discount = 10; final = 90
    assert sale.total_amount == Decimal("90.00")
