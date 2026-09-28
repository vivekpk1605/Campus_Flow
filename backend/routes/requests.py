from flask import Blueprint, g, jsonify, request

from backend.database import (
    create_leave_request,
    create_od_request,
    list_leave_requests,
    list_od_requests,
    update_leave_request,
    update_od_request,
)
from backend.middleware.auth import token_required
from backend.middleware.rbac import role_required

requests_bp = Blueprint('requests', __name__)


def payload_value(payload, key):
    return (payload.get(key) or '').strip()


@requests_bp.route('/od', methods=['GET'])
@token_required
def get_od_requests():
    requests = list_od_requests() if g.current_user['role'] == 'ADMIN' else list_od_requests(g.current_user['user_id'])
    return jsonify({'success': True, 'requests': requests}), 200


@requests_bp.route('/od', methods=['POST'])
@token_required
@role_required('STUDENT', 'FACULTY')
def submit_od_request():
    payload = request.get_json(silent=True) or {}
    required = ['purpose', 'start_date', 'end_date', 'destination', 'details']
    if not all(payload_value(payload, key) for key in required):
        return jsonify({'success': False, 'message': 'All OD fields are required.'}), 400
    item = create_od_request(
        g.current_user['user_id'],
        payload_value(payload, 'purpose'),
        payload_value(payload, 'start_date'),
        payload_value(payload, 'end_date'),
        payload_value(payload, 'destination'),
        payload_value(payload, 'details'),
        payload.get('evidence'),
    )
    return jsonify({'success': True, 'message': 'OD request submitted.', 'request': item}), 201


@requests_bp.route('/od/<int:request_id>', methods=['PUT'])
@token_required
@role_required('ADMIN')
def review_od_request(request_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get('status', 'Approved')
    if status not in {'Approved', 'Rejected'}:
        return jsonify({'success': False, 'message': 'Status must be Approved or Rejected.'}), 400
    signature = f"Digitally signed by {g.current_user['name']}"
    item = update_od_request(request_id, status, g.current_user['user_id'], signature)
    return jsonify({'success': True, 'message': 'OD request reviewed.', 'request': item}), 200


@requests_bp.route('/leave', methods=['GET'])
@token_required
def get_leave_requests():
    requests = list_leave_requests() if g.current_user['role'] == 'ADMIN' else list_leave_requests(g.current_user['user_id'])
    return jsonify({'success': True, 'requests': requests}), 200


@requests_bp.route('/leave', methods=['POST'])
@token_required
@role_required('STUDENT', 'FACULTY')
def submit_leave_request():
    payload = request.get_json(silent=True) or {}
    required = ['reason', 'start_date', 'end_date', 'details']
    if not all(payload_value(payload, key) for key in required):
        return jsonify({'success': False, 'message': 'All leave fields are required.'}), 400
    item = create_leave_request(
        g.current_user['user_id'],
        payload_value(payload, 'reason'),
        payload_value(payload, 'start_date'),
        payload_value(payload, 'end_date'),
        payload_value(payload, 'details'),
        payload.get('evidence'),
    )
    return jsonify({'success': True, 'message': 'Leave request submitted.', 'request': item}), 201


@requests_bp.route('/leave/<int:request_id>', methods=['PUT'])
@token_required
@role_required('ADMIN')
def review_leave_request(request_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get('status', 'Approved')
    if status not in {'Approved', 'Rejected'}:
        return jsonify({'success': False, 'message': 'Status must be Approved or Rejected.'}), 400
    signature = f"Digitally signed by {g.current_user['name']}"
    item = update_leave_request(request_id, status, g.current_user['user_id'], signature)
    return jsonify({'success': True, 'message': 'Leave request reviewed.', 'request': item}), 200
