import os
from flask import Flask

from config import Config
from models import User, Supplier, Product, Sale, SaleItem
from models import db

# Create the Flask application
app = Flask(__name__)

# Load the database configuration
app.config.from_object(Config)

# Create the instance directory if needed
os.makedirs(app.instance_path, exist_ok=True)

# Connect SQLAlchemy to Flask
db.init_app(app)


# Define the home page
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GreenLeaf Grocers</title>
    </head>
    <body>
        <h1>Welcome to GreenLeaf Grocers!</h1>
        <p>Inventory and Sales Management System</p>
        <p>Database setup is in progress.</p>
    </body>
    </html>
    """



# Start the development server
if __name__ == "__main__":
    app.run(debug=True)
