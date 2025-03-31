from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jti
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import datetime
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///e:/TechUnite All Data/Project-Bach-2025/API-Security-Flask/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379"
)

# Import and register the Blueprint
# from public import public_bp
# app.register_blueprint(public_bp)

# Blacklisted tokens set
blacklisted_tokens = set()

# Database Models
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    question = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Load product data
def load_products():
    with open('product.json', 'r') as file:
        return json.load(file)

# Routes

@app.route('/')
def home():
    """Home page."""
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Invalid input"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    """Login and generate JWT token."""
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Invalid input"}), 400

    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.username, expires_delta=datetime.timedelta(hours=1))
    return jsonify({"access_token": access_token}), 200


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout and blacklist the current token."""
    jti = get_jti(request.headers['Authorization'].split()[1])  # Get the token's unique identifier
    blacklisted_tokens.add(jti)
    return jsonify({"message": "Token has been revoked"}), 200

@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    """Check if a token is blacklisted."""
    return jwt_payload['jti'] in blacklisted_tokens


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Protected route that requires JWT token."""
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome, {current_user}! This is a protected route."}), 200


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback page."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_feedback = Feedback(name=name, email=email, message=message)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('feedback.html')


@app.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    """Inquiry page."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        question = request.form['question']
        new_inquiry = Inquiry(name=name, email=email, question=question)
        db.session.add(new_inquiry)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('inquiry.html')


@app.route('/oauth', methods=['GET'])
def oauth():
    """Simulate OAuth token handling (for research purposes)."""
    # This is a placeholder for OAuth implementation.
    # In a real-world scenario, you would integrate with an OAuth provider like Google or GitHub.
    return jsonify({"message": "OAuth token handling route (to be implemented)"}), 200


@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products (JWT-protected)."""
    products = load_products()
    return jsonify(products), 200

@app.route('/product/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get a single product by ID (JWT-protected)."""
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

@app.route('/add-product', methods=['POST'])
@jwt_required()
def add_product():
    """Add a new product (JWT-protected)."""
    data = request.json
    products = load_products()
    products.append(data)
    with open('product.json', 'w') as file:
        json.dump(products, file, indent=4)
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/update-product/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update an existing product (JWT-protected)."""
    data = request.json
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    product.update(data)
    with open('product.json', 'w') as file:
        json.dump(products, file, indent=4)
    return jsonify({"message": "Product updated successfully"}), 200

# Routes from public.py
@app.route('/public', methods=['GET'])
def public():
    """Public route."""
    return jsonify({"message": "This is a public route"}), 200

@app.route('/about', methods=['GET'])
def about():
    """About page."""
    return jsonify({"message": "About the API Security App"}), 200

@app.route('/contact', methods=['GET'])
def contact():
    """Contact page."""
    return jsonify({"message": "Contact us at support@example.com"}), 200

@app.route('/help', methods=['GET'])
def help():
    """Help page."""
    return jsonify({"message": "Help documentation"}), 200

@app.route('/terms', methods=['GET'])
def terms():
    """Terms and conditions."""
    return jsonify({"message": "Terms and conditions of the app"}), 200

@app.route('/privacy', methods=['GET'])
def privacy():
    """Privacy policy."""
    return jsonify({"message": "Privacy policy of the app"}), 200

@app.route('/faq', methods=['GET'])
def faq():
    """Frequently asked questions."""
    return jsonify({"message": "FAQ page"}), 200

@app.route('/status', methods=['GET'])
def status():
    """API status."""
    return jsonify({"status": "API is running"}), 200

@app.route('/features', methods=['GET'])
def features():
    """Features of the app."""
    return jsonify({"features": ["JWT Authentication", "OAuth Integration", "Rate Limiting"]}), 200

@app.route('/version', methods=['GET'])
def version():
    """API version."""
    return jsonify({"version": "1.0.0"}), 200

if __name__ == '__main__':
    app.run(debug=True)
