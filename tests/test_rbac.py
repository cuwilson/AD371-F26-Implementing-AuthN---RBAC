import os
import tempfile
import unittest
from pathlib import Path

folder = tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH'] = str(Path(folder.name) / 'test.sqlite3')
import app as demo

class RBACTests(unittest.TestCase):
    def setUp(self):
        self.client = demo.app.test_client()
        self.origin = {'Origin': 'http://localhost'}
        with demo.app.app_context():
            demo.db().execute('DELETE FROM sessions')
            demo.db().execute('DELETE FROM users')
            demo.db().commit()

    def post(self, path, data=None, headers=None):
        return self.client.post(path, json=data, headers={**self.origin, **(headers or {})})

    def test_role_enforcement_and_logout(self):
        self.assertEqual(self.client.get('/api/public').status_code, 200)
        self.assertEqual(self.client.get('/api/me').status_code, 401)
        self.assertEqual(self.client.get('/api/admin/users').status_code, 401)
        self.assertEqual(self.post('/api/register', {'username':'alice','password':'secure-demo-password','role':'Admin'}).status_code, 400)
        self.assertEqual(self.post('/api/register', {'username':'alice','password':'secure-demo-password'}).status_code, 201)
        self.assertEqual(self.post('/api/login', {'username':'alice','password':'wrong-password'}).status_code, 401)
        self.assertEqual(self.post('/api/login', {'username':'alice','password':'secure-demo-password'}).status_code, 200)
        me = self.client.get('/api/me').get_json()
        self.assertEqual(me['user']['role'], 'User')
        self.assertEqual(self.client.get('/api/admin/users').status_code, 403)
        self.assertEqual(self.post('/api/logout').status_code, 403)
        self.assertEqual(self.post('/api/logout', headers={'X-CSRF-Token':me['csrf_token']}).status_code, 200)
        self.assertEqual(self.client.get('/api/me').status_code, 401)

    def test_admin_and_origin(self):
        with demo.app.app_context():
            demo.db().execute('INSERT INTO users(username,password_hash,role,created_at) VALUES (?,?,?,?)', ('root',demo.hasher.hash('admin-test-password'),'Admin',0))
            demo.db().commit()
        self.assertEqual(self.client.post('/api/login', json={'username':'root','password':'admin-test-password'}).status_code, 403)
        self.assertEqual(self.post('/api/login', {'username':'root','password':'admin-test-password'}).status_code, 200)
        self.assertEqual(self.client.get('/api/admin/users').status_code, 200)

if __name__ == '__main__':
    unittest.main()
