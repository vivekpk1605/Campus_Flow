from functools import wraps

from flask import g, jsonify


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = g.get('current_user')
            if not user:
                return jsonify({'success': False, 'message': 'Authentication required.'}), 401
            if user.get('role') not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required role: {" or ".join(allowed_roles)}'
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
