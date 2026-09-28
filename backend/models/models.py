VALID_ROLES = ('STUDENT', 'FACULTY', 'ADMIN')

USER_COLUMNS = [
    'user_id', 'name', 'email', 'password', 'role', 'phone', 'created_at', 'updated_at'
]

ROOM_COLUMNS = [
    'room_id', 'room_number', 'building', 'floor', 'room_type', 'capacity', 'facilities', 'status'
]

ANNOUNCEMENT_COLUMNS = [
    'announcement_id', 'title', 'description', 'category', 'created_by', 'created_at', 'status'
]

EVENT_COLUMNS = [
    'event_id', 'event_name', 'description', 'event_date', 'start_time', 'end_time', 'venue', 'organizer', 'max_participants', 'status', 'created_by', 'created_at'
]

COMPLAINT_COLUMNS = [
    'complaint_id', 'user_id', 'category', 'title', 'description', 'location', 'image', 'status', 'created_at', 'updated_at'
]

LOST_FOUND_COLUMNS = [
    'item_id', 'item_name', 'description', 'category', 'location', 'date_lost', 'date_found', 'image', 'contact_information', 'item_type', 'status', 'created_by', 'created_at'
]

NOTIFICATION_COLUMNS = [
    'notification_id', 'user_id', 'title', 'message', 'is_read', 'created_at'
]


def serialize_user(row):
    if not row:
        return None
    return {
        'user_id': row['user_id'],
        'name': row['name'],
        'email': row['email'],
        'role': row['role'],
        'phone': row['phone'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


def serialize_row(row, columns=None):
    if not row:
        return None
    cols = columns or list(row.keys())
    return {key: row[key] for key in cols if key in row.keys()}
