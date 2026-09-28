import sys
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / 'frontend'
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import Config
from backend.database import CampusFlowDatabase, close_database, get_database
from backend.routes.announcements import announcements_bp
from backend.routes.auth import auth_bp
from backend.routes.complaints import complaints_bp
from backend.routes.chat import chat_bp
from backend.routes.lost_found import lost_found_bp
from backend.routes.rooms import rooms_bp
from backend.routes.requests import requests_bp
from backend.routes.users import users_bp
from backend.routes.analytics import analytics_bp


def create_app(test_config=None):
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='/app')
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    database = CampusFlowDatabase(app.config['DATABASE_URL'])
    database.initialize()
    app.extensions['database'] = database

    CORS(app, resources={r'/api/*': {'origins': '*'}})

    app.teardown_appcontext(close_database)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
    app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(lost_found_bp, url_prefix='/api/lost-found')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(requests_bp, url_prefix='/api/requests')

    @app.errorhandler(Exception)
    def handle_error(error):
        """Return JSON (not an HTML page) for any failure under /api/."""
        is_http = isinstance(error, HTTPException)
        if not is_http:
            app.logger.exception('Unhandled error on %s', request.path)
        if request.path.startswith('/api/'):
            if is_http:
                return jsonify({'success': False, 'message': error.description}), error.code
            # Debug detail. Replace with a generic message before deploying.
            return jsonify({'success': False, 'message': f'{type(error).__name__}: {error}'}), 500
        if is_http:
            return error
        return 'Internal server error', 500

    @app.route('/')
    def index():
        return redirect('/app/login.html')

    @app.route('/app')
    def frontend_root():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/app/<path:filename>')
    def frontend_file(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    @app.route('/health')
    def health():
        try:
            get_database().execute('SELECT 1').fetchone()
            return jsonify({'success': True, 'status': 'healthy'}), 200
        except Exception:
            return jsonify({'success': False, 'status': 'unhealthy'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print('CampusFlow application: http://127.0.0.1:5000/')
    # 127.0.0.1 keeps the debugger reachable only from your own machine.
    app.run(host='127.0.0.1', port=5000, debug=True)