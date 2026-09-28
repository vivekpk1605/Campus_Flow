from datetime import datetime, timedelta, timezone

import jwt
import bcrypt
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash

from backend.database import create_user, get_user_by_email

auth_bp = Blueprint('auth', __name__)


def verify_password(stored_password, password):
    if stored_password.startswith(('$2a$', '$2b$', '$2y$')):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        except ValueError:
            return False
    return check_password_hash(stored_password, password)


@auth_bp.route('/register', methods=['POST'])
def register():
    payload = request.get_json(silent=True) or {}
    name = (payload.get('name') or '').strip()
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password', '')
    role = (payload.get('role') or 'STUDENT').upper()
    phone = (payload.get('phone') or '').strip()

    if not all([name, email, password]):
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400
    if role not in {'STUDENT', 'FACULTY', 'ADMIN'}:
        return jsonify({'success': False, 'message': 'Role must be STUDENT, FACULTY, or ADMIN.'}), 400
    if get_user_by_email(email):
        return jsonify({'success': False, 'message': 'A user with this email already exists.'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = create_user(name, email, hashed_password, role, phone)
    return jsonify({'success': True, 'message': 'User registered successfully.', 'user': user}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

    user = get_user_by_email(email)
    password_matches = user and verify_password(user['password'], password)
    if not password_matches:
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    token_payload = {
        'user_id': user['user_id'],
        'role': user['role'],
        'exp': datetime.now(timezone.utc) + timedelta(minutes=current_app.config['JWT_EXPIRY_MINUTES'])
    }
    token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm=current_app.config['JWT_ALGORITHM'])

    return jsonify({'success': True, 'message': 'Login successful.', 'token': token, 'user': user}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'success': True, 'message': 'Logged out successfully.'}), 200
