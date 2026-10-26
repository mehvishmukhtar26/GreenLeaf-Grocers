
from flask import Flask

# Create the Flask application
app = Flask(__name__)


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
        <p>Our application is running successfully.</p>
    </body>
    </html>
    """


# Start the development server
if __name__ == "__main__":
    app.run(debug=True)
