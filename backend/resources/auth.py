from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Check if username or email already exists
    existing_user = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
    if existing_user:
        return jsonify(error="Username or email already exists"), 400
    
    try:
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User registered"), 201
    except IntegrityError:
        db.session.rollback()  # Rollback the session if there's an error
        return jsonify(error="An error occurred during registration"), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        # Create a JWT token with user identity (user_id)
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token), 200
    return jsonify(error="Invalid credentials"), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify(message="Successfully logged out"), 200

# Example of a protected route where we use the user_id extracted from the JWT
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()  # This ensures the user is authenticated
def profile():
    # Extract the user_id from the JWT token
    user_id = get_jwt_identity()
    
    # Query the user from the database
    user = User.query.get(user_id)
    if user:
        return jsonify(username=user.username, email=user.email), 200
    return jsonify(error="User not found"), 404
