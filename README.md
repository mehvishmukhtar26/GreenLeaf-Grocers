# GreenLeaf Grocers
## Inventory & Sales Management System with Analytics Dashboard

### Project Overview
GreenLeaf Grocers is a Python Flask-based web application designed to manage grocery store inventory, billing, sales records and business analytics.

The system helps store administrators and cashiers manage products, monitor stock levels, process customer bills and view sales performance.

### Key Features
- User login with Admin and Cashier roles.
- Product and supplier management.
- Inventory and stock quantity tracking.
- Automatic stock deduction after successful billing.
- Prevention of sales when stock is insufficient.
- Expiry date validation for products.
- Discount calculation during billing.
- Digital billing receipts.
- Low-stock alerts.
- Daily and monthly sales reports.
- Category-wise sales analytics.
- Top-selling products dashboard.
- Automated application tests.

### Technologies Used
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript
- Chart.js
- Pytest
- Git and GitHub

### Project Structure
```text
GreenLeaf-Grocers/
│
├── app.py
├── config.py
├── models/
├── routes/
├── templates/
├── static/
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_models.py
│   └── test_billing.py
│
├── instance/
├── requirements.txt
└── README.md
```

### Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/mehvishmukhtar26/GreenLeaf-Grocers.git
```

2. Open the project folder:
```bash
cd GreenLeaf-Grocers
```

3. Create a virtual environment:
```bash
python -m venv .venv
```

4. Activate the virtual environment on Windows:
```powershell
.venv\Scripts\activate
```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

6. Run the application:
```bash
python app.py
```

7. Open the local URL displayed in the terminal.

### Running Tests

Run the complete automated test suite:
```bash
python -m pytest -v
```

**Current Test Result: 14 tests passed.**

### Project Objective
The main objective is to simplify grocery store operations by providing a centralized inventory and sales management system with automated stock updates and useful business analytics.

### Developer
Developed as part of the Unified Mentor Python Developer Internship.
