from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from flask import current_app, g
import mysql.connector


class CampusFlowDatabase:
    def __init__(self, database_url):
        self.database_url = database_url

        if not self.database_url.startswith('mysql+mysqlconnector://'):
            raise ValueError('DATABASE_URL must use mysql+mysqlconnector://')

    def _connection_config(self):
        connection_url = self.database_url.removeprefix('mysql+mysqlconnector://')
        credentials, database = connection_url.split('/', 1)
        user, password_host = credentials.split(':', 1)
        password, host = password_host.rsplit('@', 1)
        host, port = (host.split(':', 1) + ['3306'])[:2]
        return {
            'user': user,
            'password': password,
            'host': host,
            'port': int(port),
            'database': database,
        }

    def get_connection(self):
        return MySQLConnection(mysql.connector.connect(**self._connection_config()))

    def initialize(self):
        conn = self.get_connection()
        schema_path = Path(__file__).resolve().parent.parent / 'database' / 'campusflow.sql'
        schema = schema_path.read_text(encoding='utf-8')
        for statement in schema.split(';'):
            statement = statement.strip()
            if statement:
                conn.execute(statement)
        conn.commit()
        conn.close()


class MySQLConnection:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def get_database():
    if 'database' not in g:
        db = current_app.extensions['database']
        g.database = db.get_connection()
    return g.database


def close_database(exception=None):
    db = g.pop('database', None)
    if db is not None:
        db.close()


def row_to_dict(row):
    if row is None:
        return None
    return {
        key: value.isoformat() if isinstance(value, (date, datetime, time))
        else str(value) if isinstance(value, timedelta)
        else value
        for key, value in dict(row).items()
    }


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def create_user(name, email, password, role, phone):
    db = get_database()
    cursor = db.execute(
        "INSERT INTO users (name, email, password, role, phone, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, email, password, role, phone, now_iso(), now_iso()),
    )
    db.commit()
    return get_user_by_id(cursor.lastrowid)


def get_user_by_id(user_id):
    row = get_database().execute('SELECT * FROM users WHERE user_id = %s', (user_id,)).fetchone()
    return row_to_dict(row)


def get_user_by_email(email):
    row = get_database().execute('SELECT * FROM users WHERE email = %s', (email,)).fetchone()
    return row_to_dict(row)


def list_users():
    rows = get_database().execute('SELECT * FROM users ORDER BY user_id DESC').fetchall()
    return [row_to_dict(row) for row in rows]


def delete_user(user_id):
    db = get_database()
    db.execute('DELETE FROM complaints WHERE user_id = %s', (user_id,))
    db.execute('DELETE FROM lost_found WHERE created_by = %s', (user_id,))
    db.execute('DELETE FROM od_requests WHERE user_id = %s', (user_id,))
    db.execute('DELETE FROM leave_requests WHERE user_id = %s', (user_id,))
    db.execute('UPDATE announcements SET created_by = NULL WHERE created_by = %s', (user_id,))
    db.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
    db.commit()


def create_announcement(title, description, category, created_by, status='Published'):
    db = get_database()
    cursor = db.execute(
        'INSERT INTO announcements (title, description, category, created_by, created_at, status) VALUES (%s, %s, %s, %s, %s, %s)',
        (title, description, category, created_by, now_iso(), status),
    )
    db.commit()
    announcement_row = db.execute('SELECT * FROM announcements WHERE announcement_id = %s', (cursor.lastrowid,)).fetchone()
    return row_to_dict(announcement_row)


def list_announcements():
    rows = get_database().execute('SELECT * FROM announcements ORDER BY announcement_id DESC').fetchall()
    return [row_to_dict(row) for row in rows]


def create_room(room_number, building, floor, room_type, capacity, facilities, status='Available'):
    db = get_database()
    cursor = db.execute(
        'INSERT INTO rooms (room_number, building, floor, room_type, capacity, facilities, status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (room_number, building, floor, room_type, capacity, facilities, status),
    )
    db.commit()
    row = db.execute('SELECT * FROM rooms WHERE room_id = %s', (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)


def list_rooms():
    rows = get_database().execute('SELECT * FROM rooms ORDER BY room_id DESC').fetchall()
    return [row_to_dict(row) for row in rows]


def create_complaint(user_id, category, title, description, location, image=None):
    db = get_database()
    cursor = db.execute(
        'INSERT INTO complaints (user_id, category, title, description, location, image, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (user_id, category, title, description, location, image, 'Submitted', now_iso(), now_iso()),
    )
    db.commit()
    row = db.execute('SELECT * FROM complaints WHERE complaint_id = %s', (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)


def list_complaints(user_id=None):
    db = get_database()
    if user_id is None:
        rows = db.execute('''
            SELECT complaints.*, users.name AS user_name, users.email AS user_email, users.role AS user_role
            FROM complaints
            LEFT JOIN users ON users.user_id = complaints.user_id
            ORDER BY complaints.complaint_id DESC
        ''').fetchall()
    else:
        rows = db.execute('SELECT * FROM complaints WHERE user_id = %s ORDER BY complaint_id DESC', (user_id,)).fetchall()
    return [row_to_dict(row) for row in rows]


def create_lost_found(item_name, description, category, location, date_lost, date_found, image, contact_information, item_type, created_by):
    db = get_database()
    cursor = db.execute(
        'INSERT INTO lost_found (item_name, description, category, location, date_lost, date_found, image, contact_information, item_type, status, created_by, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (item_name, description, category, location, date_lost, date_found, image, contact_information, item_type, 'Reported', created_by, now_iso()),
    )
    db.commit()
    row = db.execute('SELECT * FROM lost_found WHERE item_id = %s', (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)


def list_lost_found():
    rows = get_database().execute('SELECT * FROM lost_found ORDER BY item_id DESC').fetchall()
    return [row_to_dict(row) for row in rows]


def create_od_request(user_id, purpose, start_date, end_date, destination, details, evidence):
    db = get_database()
    cursor = db.execute(
        'INSERT INTO od_requests (user_id, purpose, start_date, end_date, destination, details, evidence) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (user_id, purpose, start_date, end_date, destination, details, evidence),
    )
    db.commit()
    row = db.execute('SELECT * FROM od_requests WHERE request_id = %s', (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)


def list_od_requests(user_id=None):
    db = get_database()
    if user_id is None:
        rows = db.execute('''
            SELECT od_requests.*, users.name AS user_name, users.email AS user_email, users.role AS user_role
            FROM od_requests JOIN users ON users.user_id = od_requests.user_id
            ORDER BY od_requests.request_id DESC
        ''').fetchall()
    else:
        rows = db.execute('SELECT * FROM od_requests WHERE user_id = %s ORDER BY request_id DESC', (user_id,)).fetchall()
    return [row_to_dict(row) for row in rows]


def update_od_request(request_id, status, approved_by, digital_signature):
    db = get_database()
    db.execute(
        'UPDATE od_requests SET status = %s, approved_by = %s, approved_at = %s, digital_signature = %s WHERE request_id = %s',
        (status, approved_by, now_iso(), digital_signature, request_id),
    )
    db.commit()
    row = db.execute('SELECT * FROM od_requests WHERE request_id = %s', (request_id,)).fetchone()
    return row_to_dict(row)


def create_leave_request(user_id, reason, start_date, end_date, details, evidence):
    db = get_database()
    cursor = db.execute(
        'INSERT INTO leave_requests (user_id, reason, start_date, end_date, details, evidence) VALUES (%s, %s, %s, %s, %s, %s)',
        (user_id, reason, start_date, end_date, details, evidence),
    )
    db.commit()
    row = db.execute('SELECT * FROM leave_requests WHERE request_id = %s', (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)


def list_leave_requests(user_id=None):
    db = get_database()
    if user_id is None:
        rows = db.execute('''
            SELECT leave_requests.*, users.name AS user_name, users.email AS user_email, users.role AS user_role
            FROM leave_requests JOIN users ON users.user_id = leave_requests.user_id
            ORDER BY leave_requests.request_id DESC
        ''').fetchall()
    else:
        rows = db.execute('SELECT * FROM leave_requests WHERE user_id = %s ORDER BY request_id DESC', (user_id,)).fetchall()
    return [row_to_dict(row) for row in rows]


def update_leave_request(request_id, status, approved_by, digital_signature):
    db = get_database()
    db.execute(
        'UPDATE leave_requests SET status = %s, approved_by = %s, approved_at = %s, digital_signature = %s WHERE request_id = %s',
        (status, approved_by, now_iso(), digital_signature, request_id),
    )
    db.commit()
    row = db.execute('SELECT * FROM leave_requests WHERE request_id = %s', (request_id,)).fetchone()
    return row_to_dict(row)


def analytics_summary():
    db = get_database()
    stats = {}
    stats['total_users'] = db.execute('SELECT COUNT(*) AS count FROM users').fetchone()['count']
    stats['total_students'] = db.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'STUDENT'").fetchone()['count']
    stats['total_faculty'] = db.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'FACULTY'").fetchone()['count']
    stats['total_rooms'] = db.execute('SELECT COUNT(*) AS count FROM rooms').fetchone()['count']
    stats['available_rooms'] = db.execute("SELECT COUNT(*) AS count FROM rooms WHERE status = 'Available'").fetchone()['count']
    stats['total_complaints'] = db.execute('SELECT COUNT(*) AS count FROM complaints').fetchone()['count']
    stats['resolved_complaints'] = db.execute("SELECT COUNT(*) AS count FROM complaints WHERE status = 'Resolved'").fetchone()['count']
    stats['active_complaints'] = db.execute("SELECT COUNT(*) AS count FROM complaints WHERE status IN ('Submitted', 'Assigned', 'In Progress')").fetchone()['count']
    stats['lost_items'] = db.execute("SELECT COUNT(*) AS count FROM lost_found WHERE item_type = 'Lost'").fetchone()['count']
    stats['found_items'] = db.execute("SELECT COUNT(*) AS count FROM lost_found WHERE item_type = 'Found'").fetchone()['count']
    return stats


def ensure_demo_data():
    db = get_database()
    if db.execute('SELECT COUNT(*) AS count FROM users').fetchone()['count'] == 0:
        db.execute(
            "INSERT INTO users (name, email, password, role, phone) VALUES (%s, %s, %s, %s, %s)",
            ('Admin User', 'admin@campusflow.com', 'admin123', 'ADMIN', '0000000000'),
        )
        db.commit()
