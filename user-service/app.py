from flask import Flask, request, jsonify, g
from sqlalchemy import create_engine
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from functools import wraps
import os
import jwt
from datetime import datetime, timedelta
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError, InvalidTokenError
from uuid import uuid4

from models import Base, User, RefreshToken
from user_manager import UserManager

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure structured logging format
formatter = logging.Formatter('{"time": "%(asctime)s", "service": "user-service", "level": "%(levelname)s", "message": "%(message)s"}')
logging.getLogger().handlers[0].setFormatter(formatter)

# Configure database (SQLite for simplicity)
database_url = os.environ.get('DATABASE_URL', "sqlite:///./user-service.db") # Read from environment variable
engine = create_engine(database_url)

# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(bind=engine)

@app.before_request
def create_session():
    g.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))()

@app.teardown_request
def remove_session(exception=None):
    db_session = g.pop('db_session', None)
    if db_session is not None:
        db_session.remove()

# Secret key for JWT signing (replace with a strong, securely stored key)
app.config['SECRET_KEY'] = 'your-secret-key' 

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info("Checking for authentication token")
        token = None
        # JWTs are typically sent as a Bearer token in the Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token_parts = auth_header.split()
            if len(token_parts) == 2 and token_parts[0].lower() == 'bearer':
                token = token_parts[1]

        if not token:
            logger.warning("Authentication token missing")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode and verify the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            logger.info(f"Token validated for user_id: {data.get('user_id')}")
            # Attach user data to the request context
            g.current_user = data 

        except ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except InvalidSignatureError:
            return jsonify({'message': 'Token signature is invalid'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': 'Token validation error', 'error': str(e)}), 401

        return f(*args, **kwargs)

    return decorated

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            logger.info(f"Checking for permission: {permission}")
            if not hasattr(g, 'current_user'):
                return jsonify({'message': 'User not authenticated.'}), 401 # Should be caught by @require_token, but good practice
            
            user_permissions_str = g.current_user.get('permissions', '')
            user_permissions = [p.strip() for p in user_permissions_str.split(',') if p.strip()]

            if permission not in user_permissions:
                logger.warning(f"User {g.current_user.get('username')} does not have permission: {permission}")
                return jsonify({'message': 'Insufficient permissions'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

# Authentication Endpoints

@app.route('/register', methods=['POST'])
def register_user():
    logger.info("Attempting to register a new user")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user') # Default role
    permissions = data.get('permissions', '') # Allow setting permissions during registration or manage via user update

    if not username or not password:
        logger.warning("Registration failed: Username or password missing")
        return jsonify({'message': 'Username and password are required'}), 400

    user_manager = UserManager(g.db_session)
    try:
        user_manager.create_user(username, password, role, permissions)
        g.db_session.commit()
        logger.info(f"User '{username}' registered successfully")
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        g.db_session.rollback()
        logger.error(f"Error registering user '{username}': {e}", exc_info=True)
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_manager = UserManager(g.db_session)
    user = user_manager.get_user_by_username(username)
    logger.info(f"Login attempt for username: {username}")

    if user and user_manager.verify_password(user, password):
        # Generate access token (short-lived)
        logger.info(f"Credentials valid for user '{username}'. Generating tokens.")

        access_token_expires = timedelta(minutes=15)
        access_token_claims = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'permissions': user.permissions,
            'exp': datetime.utcnow() + access_token_expires
        }
        access_token = jwt.encode(access_token_claims, app.config['SECRET_KEY'], algorithm="HS256")

        # Generate refresh token (longer-lived)
        refresh_token_expires = timedelta(days=7)
        refresh_token_jti = str(uuid4()) # Unique identifier for the refresh token
        refresh_token_claims = {
            'sub': user.id, # Subject (user ID)
            'jti': refresh_token_jti,
            'exp': datetime.utcnow() + refresh_token_expires
        }
        refresh_token = jwt.encode(refresh_token_claims, app.config['SECRET_KEY'], algorithm="HS256")

        # Store refresh token details in the database
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_jti, # Store the JTI, not the whole token string
            expires_at=datetime.utcnow() + refresh_token_expires,
            revoked=False
        )
        g.db_session.add(new_refresh_token)
        g.db_session.commit()

        logger.info(f"Tokens generated and refresh token stored for user '{username}'")
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
    else:
        logger.warning(f"Login failed for username: {username}. Invalid credentials.")
        return jsonify({'message': 'Invalid credentials'}), 401


# User Management Endpoints

# ... (Copy and adapt GET /users, GET /users/<user_id>, PUT /users/<user_id>, DELETE /users/<user_id> from original app.py) ...
# Make sure to use require_token and require_permission('user:manage') for these endpoints

# Initialize the database
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
