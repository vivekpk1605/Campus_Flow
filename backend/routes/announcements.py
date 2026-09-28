from flask import Blueprint, g, jsonify, request

from backend.database import create_announcement, list_announcements
from backend.middleware.auth import token_required
from backend.middleware.rbac import role_required

announcements_bp = Blueprint('announcements', __name__)


@announcements_bp.route('', methods=['GET'])
@token_required
def get_announcements():
    return jsonify({'success': True, 'announcements': list_announcements()}), 200


@announcements_bp.route('', methods=['POST'])
@token_required
@role_required('ADMIN')
def create_announcement_route():
    payload = request.get_json(silent=True) or {}
    announcement = create_announcement(
        title=payload.get('title', 'Untitled'),
        description=payload.get('description', 'No description provided.'),
        category=payload.get('category', 'General'),
        created_by=g.current_user['user_id'],
        status=payload.get('status', 'Published'),
    )
    return jsonify({'success': True, 'message': 'Announcement created successfully.', 'announcement': announcement}), 201
