from flask import Flask, jsonify, request
from .loan_manager import LoanManager
from .borrower_manager import BorrowerManager
from .repayment_manager import RepaymentManager
from .user_manager import UserManager
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from .models import Base, Loan, Borrower # Assuming Base is defined in models.py
from .models import RefreshToken, User
from functools import wraps, partial
import jwt, datetime, uuid, os, json

app = Flask(__name__)

# Database configuration
DATABASE_URL = "sqlite:///loan_book.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
db_session = scoped_session(SessionLocal)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your_fallback_super_secret_key') # Change this in a real application and use environment variable
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ.get('ACCESS_TOKEN_EXPIRE_SECONDS', 600)) # Default 10 minutes
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_SECONDS', 2592000)) # Default 30 days

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # check if authorization header is present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Assuming the header is in the format 'Bearer <token>' or 'token <token>'
            parts = auth_header.split()
            if parts[0].lower() == 'bearer' and len(parts) == 2:
                token = parts[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            # Decode the token (replace with your actual token validation)
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data.get('user_id') # Assuming user_id is in the token
            # Retrieve the user from the database to ensure they still exist
            user = db_session().query(User).get(user_id)
            if not user:
                return jsonify({"message": "User not found"}), 401 
            request.current_user = user  # Attach the user object to the request
 request.user_payload = data # Attach the token payload to the request
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

# Modify require_role to require_permission
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'current_user', None) # Get the user from the request object set by require_token
            # Get permissions from the token payload for potentially faster access
            user_permissions = getattr(request, 'user_payload', {}).get('permissions', [])

            # If user object is not available or permissions not in payload, fetch from user model
            if not user or not user_permissions:
                user_permissions = user.permissions.split(',') if user and user.permissions else []

            if permission not in user_permissions:
                return jsonify({"message": "Insufficient permissions"}), 403 
            return f(*args, **kwargs)
    return decorator

# Dependency to get DB session
def get_db():
    session = db_session()
    return session

@app.teardown_request
def remove_session(exception=None):
    db_session.remove()

# Apply require_token and require_permission to user management endpoints
@require_token
@require_permission('user:manage') # Example: Only users with 'user:manage' permission can list users
@app.route('/users', methods=['GET'])
def get_all_users():
    # Placeholder: Implement logic to get all users from UserManager
    session = get_db()
    user_manager = UserManager(session)
 users = user_manager.get_all_users() # Assuming UserManager has a get_all_users method
    if not users:
 return jsonify({"message": "No users found"}), 404
    # Assuming User objects can be easily serialized to JSON or have a method for it
    return jsonify([user.__dict__ for user in users]), 200

@require_token
@require_permission('user:manage') # Example: Only users with 'user:manage' permission can view user details
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Placeholder: Implement logic to get a specific user by ID from UserManager
    session = get_db()
 user_manager = UserManager(session)
 user = user_manager.get_user(user_id) # Assuming get_user method takes user_id
    if user:
        return jsonify(user.__dict__), 200
    return jsonify({"message": "User not found"}), 404

@require_token
@require_permission('user:manage') # Example: Only users with 'user:manage' permission can create users
@app.route('/users', methods=['POST'])
def create_user_admin():
    # Placeholder: Implement logic to create a new user using UserManager (for admin creation)
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    permissions = data.get('permissions', '')
    session = get_db()
 try:
 user_manager = UserManager(session)
 except Exception as e:
 return jsonify({"message": f"Error creating user manager: {e}"}), 500
    user = user_manager.create_user(username, password, role=role, permissions=permissions) # Assuming create_user handles permissions
    return jsonify({"message": "User created successfully", "user_id": user.id}), 201

@require_token
@require_permission('user:manage') # Example: Only users with 'user:manage' permission can update users
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # Placeholder: Implement logic to update user information using UserManager
    data = request.get_json()
    session = get_db()
 user_manager = UserManager(session)
    updated_user = user_manager.update_user(user_id, data)
    if updated_user:
        return jsonify(updated_user.__dict__), 200
    return jsonify({"message": "User not found"}), 404

@require_token
@require_permission('user:manage') # Example: Only users with 'user:manage' permission can delete users
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Placeholder: Implement logic to delete a user using UserManager
    session = get_db()
 user_manager = UserManager(session)
    success = user_manager.delete_user(user_id)
    if success:
        return jsonify({"message": f"User with ID: {user_id} deleted"}), 200
    return jsonify({"message": "User not found"}), 404

    return jsonify({"message": f"Endpoint to delete user with ID: {user_id}"}), 200







@require_token
@app.route('/loans', methods=['GET']) 
def get_all_loans():
    loans = LoanManager(db_session).get_all_loans()
    # Assuming Loan objects can be easily serialized to JSON or have a method for it
    # For simplicity, let's assume they have a __dict__ or can be represented as dicts
    return jsonify([loan.__dict__ for loan in loans])

@require_token
@require_permission('loan:read') # Example: Users with 'loan:read' permission can view details
@app.route('/loans/<loan_id>', methods=['GET'])
def get_loan(loan_id): 
    loan = LoanManager(db_session).get_loan(loan_id)
    if loan:
        return jsonify(loan.__dict__)
    return jsonify({"message": "Loan not found"}), 404

@require_token
@require_permission('loan:create') # Example: Users with 'loan:create' permission can create loans
@app.route('/loans', methods=['POST'])
def create_loan(): 
    data = request.get_json()
    borrower_data = data.get('borrower', {})
    loan_data = {
        'amount': data.get('amount'),
        'interest_rate': data.get('interest_rate'),
        'term': data.get('term'), 
        'start_date': data.get('start_date') # Assuming start_date is passed in a compatible format
    }
    loan = LoanManager(db_session).create_loan(borrower_data, **loan_data)
    return jsonify(loan.__dict__), 201

@require_token
@require_permission('repayment:process') # Example: Users with 'repayment:process' permission can process repayments
@app.route('/loans/<loan_id>/repay', methods=['POST'])
def process_repayment(loan_id):
    data = request.get_json()
    payment_amount = data.get('amount')
    RepaymentManager(db_session).process_repayment(loan_id, payment_amount)
    return jsonify({"message": f"Repayment processed for loan {loan_id}"}) 

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user') # Default role is 'user' 
    permissions = data.get('permissions', '') # Assuming permissions are also passed in registration
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    user_manager = UserManager(db_session)
    user = user_manager.create_user(username, password, role)
    return jsonify({"message": "User created successfully", "user_id": user.id}), 201
@app.route('/login', methods=['POST'])

def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_manager = UserManager(db_session)
    user = user_manager.get_user_by_username(username)
    # Assuming you have bcrypt or similar for password verification in UserManager
    if user and user_manager.verify_password(user, password):
        # Generate access token
        access_token_expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token_payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'permissions': user.permissions.split(',') if user.permissions else [], # Include permissions in access token
            'exp': access_token_expires
        }
        access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

        # Generate refresh token
        refresh_token_expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
        jti = str(uuid.uuid4()) # Unique identifier for the refresh token
        refresh_token_payload = {
            'user_id': user.id,
            'exp': refresh_token_expires,
            'jti': jti
        }
        refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')

        # Store refresh token in the database
        new_refresh_token = RefreshToken(user_id=user.id, token=refresh_token_payload['jti'], expires_at=refresh_token_expires)
        db = get_db()
        # Optional: Invalidate any existing valid refresh tokens for this user
        # db.query(RefreshToken).filter_by(user_id=user.id, revoked=False).update({"revoked": True})
        db.add(new_refresh_token)
        db.commit()

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    return jsonify({"message": "Invalid credentials"}), 401
@app.route('/refresh', methods=['POST'])
def refresh_access_token():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({"message": "Refresh token is missing"}), 401

    try:
        # Decode without immediate expiration check, we'll check against the database
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"], options={"verify_signature": True, "verify_exp": False})
        jti = payload.get('jti')
        user_id = payload.get('user_id')
        db = get_db()
        refresh_token_entry = db.query(RefreshToken).filter(RefreshToken.token == jti, RefreshToken.user_id == user_id, RefreshToken.expires_at > datetime.datetime.utcnow(), RefreshToken.revoked == False).first()
        if not refresh_token_entry:
            return jsonify({"message": "Invalid, expired, or revoked refresh token"}), 401

        # Generate new access token
        user = db.query(User).get(user_id)
        if not user:
             return jsonify({"message": "User not found"}), 401 # Should not happen if refresh token is valid

        access_token_expires = datetime.datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES
        access_token_payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'permissions': user.permissions.split(',') if user.permissions else [], # Include permissions in new access token
            'exp': access_token_expires
        }
        new_access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # Optional: Implement refresh token rotation
        # refresh_token_entry.revoked = True # Revoke the old refresh token
        # new_jti = str(uuid.uuid4())
        # new_refresh_token_expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
        # new_refresh_token_payload = {
        #     'user_id': user.id,
        #     'exp': new_refresh_token_expires,
        #     'jti': new_jti
        # }
        # new_refresh_token = jwt.encode(new_refresh_token_payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # new_refresh_token_entry = RefreshToken(user_id=user.id, token=new_jti, expires_at=new_refresh_token_expires)
        # db.add(new_refresh_token_entry)
        # return jsonify({"access_token": new_access_token, "refresh_token": new_refresh_token})

        return jsonify({"access_token": new_access_token})

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid refresh token"}), 401

if __name__ == '__main__':
    # Create database tables if they don't exist
    def init_db():
        Base.metadata.create_all(bind=engine)
    init_db()
    app.run(debug=True)