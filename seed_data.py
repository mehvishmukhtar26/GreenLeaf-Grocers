
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from app import app
from models import db, User, Supplier, Product, Sale, SaleItem


# Use a fixed seed so random choices are reproducible
random.seed(42)

TARGET_PRODUCTS = 64
TARGET_SALES = 550


# Products are grouped by category
PRODUCTS_BY_CATEGORY = {
    "Fruits": [
        "Apple", "Banana", "Orange", "Mango",
        "Grapes", "Pear", "Peach", "Pomegranate"
    ],
    "Vegetables": [
        "Potato", "Tomato", "Onion", "Carrot",
        "Cabbage", "Spinach", "Cucumber", "Cauliflower"
    ],
    "Dairy": [
        "Milk", "Butter", "Cheese", "Yogurt",
        "Cream", "Paneer", "Buttermilk", "Ghee"
    ],
    "Bakery": [
        "Bread", "Bun", "Cake", "Croissant",
        "Muffin", "Biscuit", "Rusk", "Pita Bread"
    ],
    "Grains": [
        "Rice", "Wheat Flour", "Oats", "Cornmeal",
        "Barley", "Lentils", "Chickpeas", "Kidney Beans"
    ],
    "Beverages": [
        "Orange Juice", "Apple Juice", "Green Tea", "Coffee",
        "Mineral Water", "Lemon Drink", "Cocoa", "Herbal Tea"
    ],
    "Snacks": [
        "Potato Chips", "Popcorn", "Peanuts", "Almonds",
        "Cashews", "Crackers", "Granola Bar", "Trail Mix"
    ],
    "Household": [
        "Dish Soap", "Laundry Detergent", "Tissue Paper",
        "Cleaning Spray", "Garbage Bags", "Sponge",
        "Hand Wash", "Floor Cleaner"
    ],
}


# Approximate price ranges in Indian rupees
PRICE_RANGES = {
    "Fruits": (20, 250),
    "Vegetables": (15, 150),
    "Dairy": (25, 180),
    "Bakery": (20, 200),
    "Grains": (35, 180),
    "Beverages": (15, 250),
    "Snacks": (10, 200),
    "Household": (20, 300),
}


SUPPLIER_NAMES = [
    "Fresh Farms Supply",
    "Valley Produce Traders",
    "Daily Dairy Distributors",
    "Sunrise Bakery Supply",
    "Golden Grain Wholesale",
    "Pure Drinks Distribution",
    "Crunchy Snacks Wholesale",
    "Clean Home Supplies",
]


def create_suppliers():
    """Create supplier records until we have eight."""
    existing_names = {
        supplier.name for supplier in Supplier.query.all()
    }

    for name in SUPPLIER_NAMES:
        if Supplier.query.count() >= 8:
            break

        if name not in existing_names:
            supplier = Supplier(
                name=name,
                phone=f"90000{random.randint(10000, 99999)}",
                email=(
                    name.lower().replace(" ", ".")
                    + "@example.com"
                ),
            )
            db.session.add(supplier)
            existing_names.add(name)

    db.session.commit()


def create_products():
    """Create 64 different products without duplicating existing names."""
    suppliers = Supplier.query.all()

    existing_names = {
        product.name for product in Product.query.all()
    }

    for category, names in PRODUCTS_BY_CATEGORY.items():
        for name in names:
            if name in existing_names:
                continue

            low, high = PRICE_RANGES[category]
            price = Decimal(
                str(round(random.uniform(low, high), 2))
            )

            # Perishable goods get an expiry date.
            if category in (
                "Fruits", "Vegetables", "Dairy", "Bakery"
            ):
                expiry_date = date.today() + timedelta(
                    days=random.randint(-5, 30)
                )
            else:
                expiry_date = date.today() + timedelta(
                    days=random.randint(30, 180)
                )

            product = Product(
                name=name,
                category=category,
                unit_price=price,
                stock_qty=random.randint(150, 300),
                reorder_level=random.randint(10, 40),
                expiry_date=expiry_date,
                supplier_id=random.choice(suppliers).supplier_id,
            )

            db.session.add(product)
            existing_names.add(name)

    db.session.commit()


def create_sales():
    """Create sales and sale items until we have 550 sales."""
    users = User.query.all()

    if not users:
        print(
            "No user accounts found. Run create_users.py first."
        )
        return

    products = Product.query.all()

    if not products:
        print("No products found. Cannot generate sales.")
        return

    # Continue from the existing number of sales if rerun.
    while Sale.query.count() < TARGET_SALES:
        available_products = [
            product for product in products
            if product.stock_qty > 0
        ]

        if not available_products:
            print("No stock remains. Cannot create more sales.")
            break

        number_of_items = min(
            random.randint(1, 4),
            len(available_products)
        )

        selected_products = random.sample(
            available_products,
            number_of_items
        )

        # Keep historical sales within the last 180 days.
        sale_date = date.today() - timedelta(
            days=random.randint(0, 179)
        )

        sale_time = time(
            hour=random.randint(8, 21),
            minute=random.randint(0, 59),
        )

        sale = Sale(
            sale_date=sale_date,
            sale_time=sale_time,
            user_id=random.choice(users).user_id,
            total_amount=Decimal("0.00"),
        )

        db.session.add(sale)
        db.session.flush()

        total = Decimal("0.00")

        for product in selected_products:
            quantity = random.randint(
                1, min(4, product.stock_qty)
            )

            item_price = Decimal(str(product.unit_price))
            line_total = item_price * quantity

            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=product.product_id,
                quantity=quantity,
                price=item_price,
            )

            db.session.add(sale_item)

            # Update stock to reflect the recorded sale.
            product.stock_qty -= quantity
            total += line_total

        sale.total_amount = total
        db.session.commit()

    print(f"Sales currently in database: {Sale.query.count()}")


def seed_database():
    """Run all seed-data operations."""
    with app.app_context():
        if User.query.count() == 0:
            print(
                "Create an admin or cashier account first "
                "by running: python create_users.py"
            )
            return

        create_suppliers()
        create_products()

        print(f"Products currently in database: {Product.query.count()}")
        print(f"Suppliers currently in database: {Supplier.query.count()}")

        if Product.query.count() < TARGET_PRODUCTS:
            print("Warning: target product count was not reached.")

        create_sales()

        print("\nSample data generation finished.")
        print(f"Products: {Product.query.count()}")
        print(f"Suppliers: {Supplier.query.count()}")
        print(f"Sales: {Sale.query.count()}")
        print(f"Sale items: {SaleItem.query.count()}")


if __name__ == "__main__":
    seed_database()
