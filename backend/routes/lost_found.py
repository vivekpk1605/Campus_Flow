from flask import Blueprint, g, jsonify, request

from backend.database import create_lost_found, list_lost_found
from backend.middleware.auth import token_required

lost_found_bp = Blueprint('lost_found', __name__)


@lost_found_bp.route('', methods=['GET'])
@token_required
def get_lost_found_items():
    return jsonify({'success': True, 'items': list_lost_found()}), 200


@lost_found_bp.route('', methods=['POST'])
@token_required
def create_item():
    payload = request.get_json(silent=True) or {}
    item = create_lost_found(
        item_name=payload.get('item_name', 'Unknown Item'),
        description=payload.get('description', 'No description provided.'),
        category=payload.get('category', 'General'),
        location=payload.get('location', 'Campus'),
        date_lost=payload.get('date_lost'),
        date_found=payload.get('date_found'),
        image=payload.get('image'),
        contact_information=payload.get('contact_information', 'N/A'),
        item_type=payload.get('item_type', 'Lost'),
        created_by=g.current_user['user_id'],
    )
    return jsonify({'success': True, 'message': 'Lost or found report submitted.', 'item': item}), 201
