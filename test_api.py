"""
Basic API integration tests for the Mealy backend.
Run with: python test_api.py
"""
import json
import os
import unittest

# Always run tests against an isolated in-memory SQLite database.
# The tests create and drop tables, so they must never point at the
# real database from .env. Set this before importing the app so it
# wins over the .env file.
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from config import db


class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'UP')

    def test_register_user(self):
        response = self.client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertEqual(data['user']['name'], 'Test User')
        self.assertEqual(data['user']['email'], 'test@example.com')

    def test_register_duplicate_email(self):
        self.client.post('/api/auth/register', json={
            'name': 'User One',
            'email': 'test@example.com',
            'password': 'password123',
        })
        response = self.client.post('/api/auth/register', json={
            'name': 'User Two',
            'email': 'test@example.com',
            'password': 'password456',
        })
        self.assertEqual(response.status_code, 409)

    def test_login_success(self):
        self.client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
        })
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

    def test_login_wrong_password(self):
        self.client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
        })
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 401)

    def test_me_endpoint(self):
        reg = self.client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
        })
        token = json.loads(reg.data)['token']

        response = self.client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user']['email'], 'test@example.com')


class TestMenuEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create admin user
            import bcrypt
            from models import User
            pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(name='Admin', email='admin@test.com', password_hash=pw, role='admin', caterer_id='test-caterer')
            db.session.add(admin)
            db.session.commit()
            self.admin_id = admin.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def _get_admin_token(self):
        response = self.client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin123',
        })
        return json.loads(response.data)['token']

    def test_list_meal_options_empty(self):
        token = self._get_admin_token()
        response = self.client.get('/api/menus/', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['mealOptions'], [])

    def test_create_meal_option(self):
        token = self._get_admin_token()
        response = self.client.post('/api/menus/', json={
            'name': 'Test Meal',
            'description': 'A test meal',
            'price': 1500,
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 201)

    def test_get_today_menu(self):
        token = self._get_admin_token()
        response = self.client.get('/api/menus/today', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['isPublished'])
        self.assertEqual(data['mealOptionIds'], [])


if __name__ == '__main__':
    unittest.main()
