# Authentication + RBAC demo

A small Flask/SQLite app with **Argon2id** passwords, **opaque server-side sessions** stored in SQLite, and three authorization levels. Python 3.10+ recommended.

## Run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m flask --app app create-admin administrator
python app.py
```

Visit http://127.0.0.1:5000/ . Create a regular account in the page, login, test the three endpoints, logout. Login as `administrator` to use the admin endpoint. The admin command prompts for the password (minimum 12 characters), without putting it in shell history.

## Routes

| Method | Path | Authorization |
|---|---|---|
| GET | `/` | Public UI |
| GET | `/api/public` | Public |
| POST | `/api/register` | Public; always creates User |
| POST | `/api/login` | Public |
| GET | `/api/me` | User or Admin |
| GET | `/api/admin/users` | Admin only |
| POST | `/api/logout` | Logged in; CSRF token required |

Authorization is enforced **server-side**, not by frontend button visibility. Unauthorized users receive 401; authenticated non-admins receive 403. `role` is never read from cookies or trusted from user input: roles come from SQLite at each request. Session tokens are random, stored **only hashed** on the server, and immediately revoked on logout. Login rotates an existing session. Cookie is `HttpOnly`, `SameSite=Strict`, with `Secure` enabled using `COOKIE_SECURE=1` for HTTPS deployments.

## Security and deployment notes

- This demo requires an exact same-origin `Origin` header on all mutating requests (including `POST` register/login); browser `fetch()` supplies it. This is not intended as a general cross-origin API. Logout also checks a CSRF token issued to the authenticated page by `/api/me`.
- Use TLS and `COOKIE_SECURE=1` for any deployment beyond localhost. Do not expose Flask's development server to the internet; use a production WSGI server and reverse proxy with trusted host configuration.
- Set an explicit trusted host / reverse-proxy origin policy before deploying; `request.host_url` assumes the Host header is validated by infrastructure. For a public app, configure host allowlisting, rate limiting, account recovery, security monitoring, session management, and DB backup/migrations. Keep the SQLite file private.
- The demo is intentionally small: it does not implement brute-force throttling, email confirmation, password reset, MFA, a full CSRF framework, or admin audit trails. Do not represent it as production-ready.
- `GET /api/me` includes a CSRF token used only for unsafe methods; protect same-origin script content from XSS (CSP is included). Don't put authentication tokens in localStorage.

## Quick test

```bash
python -m unittest discover -s tests -v
```
