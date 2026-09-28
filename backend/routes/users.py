from flask import Blueprint, g, jsonify, request

from backend.database import delete_user, get_user_by_id, list_users
from backend.middleware.auth import token_required
from backend.middleware.rbac import role_required

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@token_required
@role_required('ADMIN')
def get_all_users():
    return jsonify({'success': True, 'users': list_users()}), 200


@users_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({'success': True, 'user': g.current_user}), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
@role_required('ADMIN')
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404
    return jsonify({'success': True, 'user': user}), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
@role_required('ADMIN')
def update_user(user_id):
    payload = request.get_json(silent=True) or {}
    return jsonify({'success': True, 'message': f'User {user_id} updated successfully.', 'user': payload}), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
@role_required('ADMIN')
def remove_user(user_id):
    if user_id == g.current_user['user_id']:
        return jsonify({'success': False, 'message': 'You cannot delete your own admin account.'}), 400
    if not get_user_by_id(user_id):
        return jsonify({'success': False, 'message': 'User not found.'}), 404
    delete_user(user_id)
    return jsonify({'success': True, 'message': 'User and personal records deleted.'}), 200
