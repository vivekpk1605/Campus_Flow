from flask import Blueprint, jsonify, request

from backend.database import create_room, list_rooms
from backend.middleware.auth import token_required
from backend.middleware.rbac import role_required

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('', methods=['GET'])
@token_required
def list_all_rooms():
    return jsonify({'success': True, 'rooms': list_rooms()}), 200


@rooms_bp.route('/available', methods=['GET'])
@token_required
def list_available_rooms():
    rooms = [room for room in list_rooms() if room.get('status') == 'Available']
    return jsonify({'success': True, 'rooms': rooms}), 200


@rooms_bp.route('', methods=['POST'])
@token_required
@role_required('ADMIN')
def add_room():
    payload = request.get_json(silent=True) or {}
    room = create_room(
        room_number=payload.get('room_number', 'N/A'),
        building=payload.get('building', 'Main Block'),
        floor=int(payload.get('floor', 1)),
        room_type=payload.get('room_type', 'Classroom'),
        capacity=int(payload.get('capacity', 0)),
        facilities=payload.get('facilities', 'Basic'),
        status=payload.get('status', 'Available'),
    )
    return jsonify({'success': True, 'message': 'Room added successfully.', 'room': room}), 201
