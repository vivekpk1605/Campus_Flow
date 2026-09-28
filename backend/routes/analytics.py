from flask import Blueprint, jsonify

from backend.database import analytics_summary
from backend.middleware.auth import token_required
from backend.middleware.rbac import role_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics', methods=['GET'])
@token_required
@role_required('ADMIN')
def get_analytics():
    stats = analytics_summary()
    return jsonify({'success': True, 'analytics': stats}), 200
