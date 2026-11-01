"""Minimal RBAC demo: Flask, SQLite, Argon2id, opaque server-side sessions."""
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from datetime import timedelta
from functools import wraps
from pathlib import Path

import click
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from flask import Flask, g, jsonify, request, send_from_directory

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('DATABASE_PATH', str(BASE / 'rbac.sqlite3')))
COOKIE = 'rbac_session'
SESSION_SECONDS = 8 * 60 * 60
hasher = PasswordHasher()  # Argon2id, salted, parameterized

app = Flask(__name__, static_folder=None)
app.config.update(
    MAX_CONTENT_LENGTH=8192,
    SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE', '0') == '1',
)


def db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'User' CHECK(role IN ('User', 'Admin')),
                created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                csrf_token TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at);
        ''')
        connection.commit()
    finally:
        connection.close()


def session_digest(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def public_user(user):
    return {'id': user['id'], 'username': user['username'], 'role': user['role']}


def json_body():
    if not request.is_json:
        return None
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@app.before_request
def load_session_and_validate_origin():
    g.user = None
    g.auth_session = None
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        # Only browser requests originating from this application can change state.
        # Requiring an Origin header is intentional for this browser-oriented demo.
        origin = request.headers.get('Origin')
        expected = request.host_url.rstrip('/')
        if origin != expected:
            return jsonify(error='Invalid or missing Origin header'), 403
    token = request.cookies.get(COOKIE)
    if token:
        record = db().execute('''
            SELECT s.csrf_token, s.expires_at, u.id, u.username, u.role
            FROM sessions s JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
        ''', (session_digest(token), int(time.time()))).fetchone()
        if record:
            g.auth_session = record
            g.user = record


def require_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if g.user is None:
            return jsonify(error='Authentication required'), 401
        return fn(*args, **kwargs)
    return wrapper


def require_role(role):
    def decorate(fn):
        @wraps(fn)
        @require_login
        def wrapper(*args, **kwargs):
            if g.user['role'] != role:
                return jsonify(error='Forbidden: Admin role required'), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorate


def csrf_valid():
    supplied = request.headers.get('X-CSRF-Token', '')
    return bool(g.auth_session and supplied and hmac.compare_digest(supplied, g.auth_session['csrf_token']))


def set_session(response, user_id):
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    db().execute('INSERT INTO sessions(token_hash, user_id, csrf_token, expires_at) VALUES (?, ?, ?, ?)',
                 (session_digest(token), user_id, csrf, int(time.time()) + SESSION_SECONDS))
    db().commit()
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, httponly=True,
                        secure=app.config['SESSION_COOKIE_SECURE'], samesite='Strict', path='/')
    return response


@app.get('/')
def index():
    return send_from_directory(BASE / 'static', 'index.html')


@app.get('/static/app.js')
def static_js():
    return send_from_directory(BASE / 'static', 'app.js')


@app.get('/api/public')
def public():
    return jsonify(message='Public content: accessible without a session')


@app.post('/api/register')
def register():
    data = json_body()
    if data is None or set(data) - {'username', 'password', 'role'}:
        return jsonify(error='Expected JSON with username and password'), 400
    username, password = data.get('username'), data.get('password')
    if not isinstance(username, str) or not (3 <= len(username) <= 32) or not username.isascii() or not all(c.isalnum() or c == '_' for c in username):
        return jsonify(error='Username must be 3-32 ASCII letters, digits or underscores'), 400
    if not isinstance(password, str) or not 12 <= len(password) <= 256:
        return jsonify(error='Password must be 12-256 characters'), 400
    # Never accept a client-supplied role: public registrations are User only.
    if 'role' in data:
        return jsonify(error='Role cannot be set during registration'), 400
    try:
        cur = db().execute('INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
                           (username, hasher.hash(password), 'User', int(time.time())))
        db().commit()
    except sqlite3.IntegrityError:
        return jsonify(error='Username unavailable'), 409
    return jsonify(message='Registered successfully', user={'id': cur.lastrowid, 'username': username, 'role': 'User'}), 201


@app.post('/api/login')
def login():
    data = json_body()
    if data is None or not isinstance(data.get('username'), str) or not isinstance(data.get('password'), str):
        return jsonify(error='Expected username and password'), 400
    username, password = data['username'], data['password']
    if len(username) > 256 or len(password) > 256:
        return jsonify(error='Invalid credentials'), 401
    user = db().execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    verified = False
    if user:
        try:
            verified = hasher.verify(user['password_hash'], password)
        except (VerificationError, InvalidHashError):
            pass
    if not verified:
        return jsonify(error='Invalid credentials'), 401
    if hasher.check_needs_rehash(user['password_hash']):
        db().execute('UPDATE users SET password_hash = ? WHERE id = ?', (hasher.hash(password), user['id']))
        db().commit()
    # Revoke the current session if signing into a different account.
    old = request.cookies.get(COOKIE)
    if old:
        db().execute('DELETE FROM sessions WHERE token_hash = ?', (session_digest(old),))
        db().commit()
    response = jsonify(message='Logged in', user=public_user(user))
    return set_session(response, user['id'])


@app.get('/api/me')
@require_login
def me():
    return jsonify(user=public_user(g.user), csrf_token=g.auth_session['csrf_token'])


@app.get('/api/admin/users')
@require_role('Admin')
def admin_users():
    records = db().execute('SELECT id, username, role FROM users ORDER BY id LIMIT 100').fetchall()
    return jsonify(users=[public_user(u) for u in records])


@app.post('/api/logout')
@require_login
def logout():
    if not csrf_valid():
        return jsonify(error='Invalid CSRF token'), 403
    token = request.cookies.get(COOKIE)
    db().execute('DELETE FROM sessions WHERE token_hash = ?', (session_digest(token),))
    db().commit()
    response = jsonify(message='Logged out')
    response.delete_cookie(COOKIE, path='/')
    return response


@app.after_request
def security_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
    return response


@app.cli.command('create-admin')
@click.argument('username')
@click.password_option(confirmation_prompt=True)
def create_admin(username, password):
    """Create a privileged account via trusted CLI, never via HTTP."""
    if not 3 <= len(username) <= 32 or not username.isascii() or not all(c.isalnum() or c == '_' for c in username):
        raise click.ClickException('Username must be 3-32 ASCII letters, digits or underscores')
    if not 12 <= len(password) <= 256:
        raise click.ClickException('Password must be 12-256 characters')
    init_db()
    try:
        db().execute('INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, ?, ?)',
                     (username, hasher.hash(password), 'Admin', int(time.time())))
        db().commit()
    except sqlite3.IntegrityError as exc:
        raise click.ClickException('Username unavailable') from exc
    click.echo('Admin account created')


init_db()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
