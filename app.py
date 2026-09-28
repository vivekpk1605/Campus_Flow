import logging

from flask import cli

from backend.app import create_app


if __name__ == '__main__':
    cli.show_server_banner = lambda *args, **kwargs: None
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app = create_app()
    print('CampusFlow application: http://127.0.0.1:5000/')
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
