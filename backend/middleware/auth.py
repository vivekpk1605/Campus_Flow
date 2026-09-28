from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from backend.database import get_user_by_id


def _decode_token(token):
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=[current_app.config['JWT_ALGORITHM']])


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authorization token is missing.'}), 401

        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return jsonify({'success': False, 'message': 'Authorization token is invalid.'}), 401

        try:
            payload = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid JWT token.'}), 401

        user = get_user_by_id(payload.get('user_id'))
        if not user:
            return jsonify({'success': False, 'message': 'User not found for token.'}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated
