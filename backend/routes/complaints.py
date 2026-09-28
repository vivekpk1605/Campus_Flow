from flask import Blueprint, g, jsonify, request

from backend.database import create_complaint, list_complaints
from backend.middleware.auth import token_required
from backend.middleware.rbac import role_required

complaints_bp = Blueprint('complaints', __name__)


@complaints_bp.route('', methods=['GET'])
@token_required
@role_required('ADMIN')
def get_all_complaints():
    return jsonify({'success': True, 'complaints': list_complaints()}), 200


@complaints_bp.route('/my', methods=['GET'])
@token_required
@role_required('STUDENT', 'FACULTY')
def get_my_complaints():
    return jsonify({'success': True, 'complaints': list_complaints(user_id=g.current_user['user_id'])}), 200


@complaints_bp.route('', methods=['POST'])
@token_required
@role_required('STUDENT', 'FACULTY')
def submit_complaint():
    payload = request.get_json(silent=True) or {}
    complaint = create_complaint(
        user_id=g.current_user['user_id'],
        category=payload.get('category', 'Other'),
        title=payload.get('title', 'Complaint'),
        description=payload.get('description', 'No description'),
        location=payload.get('location', 'Campus'),
        image=payload.get('image'),
    )
    return jsonify({'success': True, 'message': 'Complaint submitted successfully.', 'complaint': complaint}), 201


@complaints_bp.route('/<int:complaint_id>/status', methods=['PUT'])
@token_required
@role_required('ADMIN')
def update_complaint_status(complaint_id):
    payload = request.get_json(silent=True) or {}
    new_status = payload.get('status', 'Submitted')
    return jsonify({'success': True, 'message': f'Complaint {complaint_id} status updated to {new_status}.', 'status': new_status}), 200
