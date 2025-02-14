from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from functools import wraps
import jwt
from jwt import ExpiredSignatureError  # Import ExpiredSignatureError from PyJWT
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

SECRET_KEY = "12345678"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        
        try:
            token = token.split("Bearer ")[1]  # Extract actual token
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return f(decoded, *args, **kwargs)
        except ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please log in again."}), 401
        except Exception as e:
            return jsonify({"error": "Invalid token format."}), 401
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Default role is 'user'

    if not username or not password:
        return jsonify({"error": "Username and Password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify(token=access_token), 200

@app.route('/api/services', methods=['GET'])
@token_required
def get_services(user):
    services = {
        'cleaning': [
            {'id': 1, 'name': 'House Cleaning', 'price': 3500},
            {'id': 2, 'name': 'Couch Cleaning', 'price': 2500},
            {'id': 3, 'name': 'Toilet Cleaning', 'price': 3000},
            {'id': 4, 'name': 'Car Cleaning', 'price': 1200},
            {'id': 5, 'name': 'Laundry', 'price': 2000},
            {'id': 6, 'name': 'Dry Cleaning', 'price': 1500},
        ],
        'food': [
            {'id': 1, 'name': 'Fries', 'price': 170},
            {'id': 2, 'name': 'KFC', 'price': 230},
            {'id': 3, 'name': 'Smokies', 'price': 50},
            {'id': 4, 'name': 'Hotdog', 'price': 300},
            {'id': 5, 'name': 'Sausages', 'price': 50},
            {'id': 6, 'name': 'Bread', 'price': 65},
            {'id': 7, 'name': 'Cakes', 'price': 1500},
            {'id': 8, 'name': 'Meat', 'price': 600},
            {'id': 9, 'name': 'Fish', 'price': 750},
            {'id': 10, 'name': 'Chicken', 'price': 700},
            {'id': 11, 'name': 'Blended Juice', 'price': 250},
        ],
        'groceries': [
            {'id': 1, 'name': 'Onions', 'price': 50},
            {'id': 2, 'name': 'Tomato', 'price': 50},
            {'id': 3, 'name': 'Pepper', 'price': 50},
            {'id': 4, 'name': 'Kales', 'price': 50},
            {'id': 5, 'name': 'Cabbages', 'price': 50},
            {'id': 6, 'name': 'Green Pepper', 'price': 50},
            {'id': 7, 'name': 'Coriander', 'price': 50},
        ],
        'fruit': [
            {'id': 1, 'name': 'Mango', 'price': 100},
            {'id': 2, 'name': 'Banana', 'price': 100},
            {'id': 3, 'name': 'Watermelon', 'price': 350},
            {'id': 4, 'name': 'Grapes', 'price': 300},
            {'id': 5, 'name': 'Strawberry', 'price': 300},
        ],
        'gardening': [
            {'id': 1, 'name': 'Garbage Collection', 'price': 200},
            {'id': 2, 'name': 'Landscaping', 'price': 1000},
        ]
    }
    return jsonify(services), 200

@app.route('/api/orders/my', methods=['GET'])
@token_required
def get_user_orders(user):
    user_id = user["id"]
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "order_id": order.id,
        "service_id": order.service_id,
        "quantity": order.quantity,
        "location": order.location,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    } for order in orders]), 200

@app.route('/api/orders', methods=['POST'])
@token_required
def place_order(user):
    data = request.json
    service_id = data.get("service_id")
    quantity = data.get("quantity", 1)
    location = data.get("location", "")
    total_price = data.get("total_price", 0.0)

    if not service_id:
        return jsonify({"error": "Service ID is required"}), 400

    order = Order(
        user_id=user["id"],
        service_id=service_id,
        quantity=quantity,
        location=location,
        total_price=total_price,
        status="Pending"
    )
    db.session.add(order)
    db.session.commit()
    
    return jsonify({"message": "Order placed successfully", "order": {
        "order_id": order.id,
        "service_id": order.service_id,
        "quantity": order.quantity,
        "location": order.location,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    }}), 201

@app.route('/api/orders', methods=['GET'])
@token_required
def get_all_orders(user):
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    orders = Order.query.all()
    return jsonify([{
        "order_id": order.id,
        "user_id": order.user_id,
        "service_id": order.service_id,
        "quantity": order.quantity,
        "location": order.location,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    } for order in orders]), 200

@app.route('/api/orders/<int:order_id>/confirm', methods=['POST'])
@token_required
def confirm_order(user, order_id):
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order.status = "Confirmed"
    db.session.commit()
    
    return jsonify({"message": "Order confirmed successfully", "order": {
        "order_id": order.id,
        "service_id": order.service_id,
        "quantity": order.quantity,
        "location": order.location,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat()
    }}), 200

if __name__ == '__main__':
    app.run(debug=True)