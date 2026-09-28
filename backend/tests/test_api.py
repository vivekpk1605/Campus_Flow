import os
from uuid import uuid4

import pytest

from backend.app import create_app


@pytest.fixture
def client():
    database_url = os.getenv('DATABASE_URL')
    if not database_url or not database_url.startswith('mysql+mysqlconnector://'):
        pytest.fail('DATABASE_URL must point to MySQL for integration tests')
    app = create_app({'TESTING': True, 'DATABASE_URL': database_url})
    with app.test_client() as client:
        yield client


def test_register_and_login_student(client):
    email = f'alice-{uuid4().hex}@example.com'
    res = client.post('/api/auth/register', json={
        'name': 'Alice Student',
        'email': email,
        'password': 'Password123!',
        'role': 'STUDENT',
        'phone': '1234567890'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True

    login = client.post('/api/auth/login', json={
        'email': email,
        'password': 'Password123!'
    })
    assert login.status_code == 200
    token = login.get_json()['token']
    assert token

    me = client.get('/api/users/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200
    assert me.get_json()['user']['email'] == email


def test_admin_only_route_rejected_for_student(client):
    email = f'student-{uuid4().hex}@example.com'
    client.post('/api/auth/register', json={
        'name': 'Student One',
        'email': email,
        'password': 'Password123!',
        'role': 'STUDENT',
        'phone': '1111111111'
    })
    login = client.post('/api/auth/login', json={
        'email': email,
        'password': 'Password123!'
    })
    token = login.get_json()['token']

    res = client.get('/api/analytics', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 403
    assert res.get_json()['success'] is False


def test_admin_can_create_announcement(client):
    email = f'admin-{uuid4().hex}@example.com'
    client.post('/api/auth/register', json={
        'name': 'Admin User',
        'email': email,
        'password': 'Password123!',
        'role': 'ADMIN',
        'phone': '9999999999'
    })
    login = client.post('/api/auth/login', json={
        'email': email,
        'password': 'Password123!'
    })
    token = login.get_json()['token']

    res = client.post('/api/announcements', headers={'Authorization': f'Bearer {token}'}, json={
        'title': 'Orientation',
        'description': 'Welcome event',
        'category': 'Academic',
        'status': 'Published'
    })
    assert res.status_code == 201
    assert res.get_json()['announcement']['title'] == 'Orientation'
