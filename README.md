# AD371 – Authentication & Role-Based Access Control (RBAC)

**Course:** AD371 – Software Architecture  
**Semester:** Fall 2026

## Project Overview

This project is a lightweight web application demonstrating Authentication (AuthN) and Role-Based Access Control (RBAC). It was initially generated using ChatGPT and then reviewed, tested, and modified to address security issues and deployment requirements.

The application allows users to register, log in, access protected information, and log out. It uses two roles:

- **User:** Can register, log in, and access protected resources.
- **Admin:** Can access protected resources and restricted administrative information.

The project also includes a public endpoint that can be accessed without authentication.

The goal of this assignment was to evaluate AI-generated security code, identify weaknesses, implement improvements, and verify the application through functional and security testing.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python / Flask | Backend application and REST API |
| HTML, CSS, JavaScript | Frontend interface |
| Neon PostgreSQL | Hosted database for users and sessions |
| SQLite | Local development and automated testing |
| Argon2id | Secure password hashing |
| Flask-Limiter | Login rate limiting |
| Psycopg | PostgreSQL database connection |
| Vercel | Application hosting and deployment |
| GitHub | Source control and documentation |

## Application Architecture

The application follows a client-server architecture with server-side authentication and authorization.

**Architecture Flow:**

1. The user interacts with the HTML/JavaScript frontend hosted on Vercel.
2. The frontend sends HTTP requests to the Flask API.
3. Flask validates the submitted information and checks authentication.
4. Neon PostgreSQL stores user accounts, password hashes, roles, and sessions.
5. Server-side middleware determines whether the authenticated user has permission to access the requested endpoint.
6. Flask returns the appropriate HTTP response.

The application uses SQLite for local development and testing, while the deployed version uses Neon PostgreSQL.

### Authentication and Authorization

**Authentication (AuthN)** verifies the user's identity through their username and password. Passwords are hashed using Argon2id, and successful authentication creates a server-side session.

**Authorization (AuthZ)** determines what an authenticated user is allowed to access. Flask decorators enforce role restrictions on protected endpoints.

Authorization is handled on the backend rather than relying on hidden frontend buttons.

### API Endpoints

| Method | Endpoint | Access |
|---|---|---|
| GET | `/` | Public frontend |
| GET | `/api/public` | Public |
| POST | `/api/register` | Public registration |
| POST | `/api/login` | Public login |
| GET | `/api/me` | Authenticated users |
| GET | `/api/admin/users` | Admin only |
| POST | `/api/logout` | Authenticated users |

### HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Account created successfully |
| 400 | Invalid input |
| 401 | Authentication required or invalid credentials |
| 403 | Access forbidden |
| 409 | Username unavailable |
| 429 | Too many login requests |

## Installation and Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/cuwilson/AD371-F26-Implementing-AuthN---RBAC.git
cd AD371-F26-Implementing-AuthN---RBAC
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows Command Prompt:**

```cmd
.venv\Scripts\activate.bat
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:

- Flask
- argon2-cffi
- Flask-Limiter
- psycopg

### 4. Database Configuration

The application supports two database configurations.

**SQLite (Local Development)**

When no `DATABASE_URL` environment variable is configured, the application automatically uses a local SQLite database named `rbac.sqlite3`.

**Neon PostgreSQL (Deployment)**

When `DATABASE_URL` is configured, the application connects to the Neon PostgreSQL database.

The connection string is stored in environment variables rather than hardcoded into the application.

Example variable:

```env
DATABASE_URL=your_postgresql_connection_string
```

The actual connection string must not be committed to GitHub.

The local `.env.local` file, SQLite database files, and virtual environment are excluded from source control.

For PostgreSQL, the database tables can be initialized with:

```cmd
python -m flask --app app init-db
```

This command requires `DATABASE_URL` to be present in the process environment.

### 5. Create an Admin Account

```cmd
python -m flask --app app create-admin administrator
```

Enter and confirm a password of at least 12 characters.

Admin accounts are created through the command-line interface rather than through public registration.

### 6. Start the Application

```cmd
python app.py
```

Open:

http://127.0.0.1:5000/

The application provides controls for registration, login, logout, and testing the public, protected, and Admin endpoints.

## Vercel Deployment

The application is deployed using Vercel, with Neon PostgreSQL providing persistent database storage.

**Live Application:** Add Vercel deployment URL here

**GitHub Repository:**  
https://github.com/cuwilson/AD371-F26-Implementing-AuthN---RBAC

### Deployment Configuration

1. Connect the GitHub repository to Vercel.
2. Configure the application as a Python/Flask project.
3. Connect a Neon PostgreSQL database using the Vercel Marketplace integration.
4. Verify that `DATABASE_URL` is available in the deployment environment.
5. Initialize the PostgreSQL database and create an Admin account through a trusted local CLI connection.
6. Deploy the application and verify the live API endpoints.

Neon stores user accounts and sessions persistently, allowing the application to maintain authentication information across Vercel requests and deployments.

The application uses secure session cookies in the Vercel HTTPS environment.

## AI Disclosure and Prompt Appendix

### AI Tool Used

**ChatGPT (OpenAI)**

ChatGPT was used to generate the initial application, including the Flask backend, SQLite database, authentication functions, authorization middleware, and frontend interface.

ChatGPT was also used to assist with the security audit, debugging, PostgreSQL migration, Vercel deployment, and documentation.

The generated code was reviewed and tested rather than assumed to be secure.

### Original AI Prompt

The following prompt was provided directly by the assignment instructions and used to generate the initial application:

> Act as a senior security engineer. Build a lightweight full-stack application (or REST API with a simple frontend) demonstrating basic Authentication and Role-Based Access Control (RBAC).
>
> The application must include:
>
> 1. User Registration & Login with two roles: 'User' and 'Admin'.
> 2. Password hashing using a modern, secure algorithm.
> 3. Token-based (JWT) or Session-based authentication.
> 4. Three distinct views or API endpoints:
>
>    - Public: Accessible to anyone (e.g., home/landing page).
>    - Protected (User): Accessible to any authenticated user (e.g., user profile or dashboard).
>    - Restricted (Admin Only): Accessible ONLY to users with the 'Admin' role (e.g., user management list or system metrics).
>
> Provide the backend server code, route-guard middleware, and a minimal frontend or HTML/JS interface to test registration, login, logout, and role access.

### Additional AI Assistance

After generating the initial application, ChatGPT was used through follow-up conversations to:

- Review the original application against the security checklist.
- Identify missing login rate limiting.
- Implement Flask-Limiter.
- Diagnose and correct Content Security Policy violations.
- Migrate the application from SQLite-only storage to SQLite/PostgreSQL support.
- Troubleshoot PostgreSQL SQL parameter differences.
- Configure Neon PostgreSQL for Vercel.
- Prepare QA tests and documentation.

The original implementation is preserved in Git history for comparison with the corrected version.

## Security Audit

The initial AI-generated application implemented several important security practices correctly. However, additional review identified areas requiring improvements.

### 1. Password Storage — Passed

The application uses Argon2id password hashing through the `argon2-cffi` package.

Passwords are salted and hashed before storage. During login, the submitted password is verified against the stored hash.

Database inspection of the local SQLite implementation confirmed that passwords were stored as Argon2id hashes rather than plaintext.

**Correction:** None required.

### 2. Server-Side Authorization — Passed

The application uses backend decorators to enforce authentication and authorization.

- `require_login` checks whether a valid authenticated session exists.
- `require_role` verifies that the user has the necessary role.

A standard User attempting to access the Admin endpoint receives HTTP 403. An Admin accessing the same endpoint receives HTTP 200.

These restrictions are enforced by Flask rather than by hiding frontend controls.

**Correction:** None required.

### 3. Login Rate Limiting — Improved

**Issue identified:**

The original AI-generated application did not limit repeated login attempts, allowing unrestricted request frequency.

**Correction:**

Added Flask-Limiter to the login endpoint:

```python
@app.post('/api/login')
@limiter.limit('5 per minute')
def login():
```

This limits requests to five per minute per client IP address for a single application instance.

**Verification:**

During local testing, six consecutive incorrect login attempts were submitted. The first five returned HTTP 401, and the sixth returned HTTP 429.

**Limitation:**

The implementation uses in-memory storage, which does not synchronize rate limits across multiple Vercel serverless instances. The rate limit was verified locally but is not guaranteed to behave consistently across distributed production instances.

### 4. Content Security Policy — Fixed

**Issue identified:**

The original AI-generated frontend contained an inline CSS `<style>` block while also implementing a Content Security Policy restricting styles to `'self'`.

This caused the browser to block the inline stylesheet and display CSP violations in Developer Tools.

**Correction:**

- Created `static/style.css`.
- Moved the CSS out of `index.html`.
- Updated the HTML to reference the external stylesheet.
- Added a Flask route for the CSS file.

**Verification:**

The frontend styling loaded correctly, and the original CSP errors were resolved.

This correction allowed the application to retain its restrictive Content Security Policy without enabling unsafe inline styles.

### 5. Session Security — Passed Code Review

The application uses opaque server-side session tokens rather than storing authentication details in the frontend.

Security features include:

- Cryptographically random session tokens.
- Hashed session identifiers stored in the database.
- HttpOnly cookies.
- SameSite=Strict cookie settings.
- Secure cookies for HTTPS deployments.
- Session expiration.
- Server-side session revocation during logout.
- CSRF protection for logout requests.

### 6. Sensitive Data and Error Handling — Passed

The application returns generic login errors rather than identifying whether a username exists.

Administrative API responses include usernames and roles but do not expose stored password hashes.

SQL queries use parameterized inputs to prevent submitted values from being interpreted as SQL commands.

### Security Audit Summary

| Requirement | Result |
|---|---|
| Argon2id password hashing | Passed |
| Salted password storage | Passed |
| Server-side authentication | Passed |
| Server-side RBAC | Passed |
| Generic login errors | Passed |
| Sensitive data excluded from responses | Passed |
| Secure session handling | Passed code review |
| Login rate limiting | Improved |
| Content Security Policy | Fixed |
| Server-side input validation | Passed |
| Parameterized SQL queries | Passed code review |

## Quality Assurance Testing

The application was tested locally and against the deployed Vercel environment.

### Authentication Tests

| Test | Expected Result | Status |
|---|---|---|
| Register a new account | HTTP 201, User role assigned | Pass |
| Login with valid credentials | HTTP 200, authenticated session | Pass |
| Login with incorrect password | HTTP 401, generic error | Pass |
| Logout | Session invalidated | Pass |
| Access protected endpoint after logout | HTTP 401 | Pass |

### Authorization Tests

| Test | Expected Result | Status |
|---|---|---|
| Public endpoint without login | HTTP 200 | Pass |
| User accesses protected profile | HTTP 200 | Pass |
| User attempts Admin endpoint | HTTP 403 | Pass |
| Admin accesses Admin endpoint | HTTP 200 | Pass |
| Unauthenticated access to protected endpoint | HTTP 401 | Pass |

### Input Validation and Security Tests

| Test | Expected Result | Status |
|---|---|---|
| Empty registration fields | Client rejects submission | Pass |
| Direct API request with empty fields | HTTP 400 | Pass |
| SQL-like login input | HTTP 401, no authentication bypass | Pass |
| Inspect local stored passwords | Argon2id hashes | Pass |
| Six rapid login requests (local) | HTTP 429 on sixth attempt | Pass |
| Inspect Admin API response | No password hashes exposed | Pass |
| Inspect deployed Neon password hashes | Hashed storage confirmed | Pass |

### Browser Console and Network Testing

Browser Developer Tools were used to verify API responses and investigate frontend errors.

The following responses were observed:

- HTTP 200 — Successful public and authenticated requests.
- HTTP 201 — Successful registration.
- HTTP 400 — Invalid registration input.
- HTTP 401 — Unauthenticated access or invalid credentials.
- HTTP 403 — Restricted Admin access.
- HTTP 429 — Local login rate limit exceeded.

The original Content Security Policy errors were identified and corrected.

An HTTP 401 response from `/api/me` while logged out is expected because the frontend automatically checks authentication status.

No unexpected unhandled JavaScript exceptions were reported during the completed local checks. Final deployed browser-console inspection remains to be confirmed.

### Automated Testing

The project includes automated unit tests using Python's built-in `unittest` framework.

Run the tests with:

```cmd
python -m unittest discover -s tests -v
```

**Test Results:**

```text
test_admin_and_origin ... ok
test_role_enforcement_and_logout ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.255s

OK
```

**Result: 2 tests passed, 0 failures.**

The automated tests verify authentication, authorization, logout behavior, and request-origin validation using the local test database.

## Limitations and Future Improvements

This application is intended as an educational security demonstration rather than a production-ready authentication platform.

Additional improvements for a production environment would include:

- Shared rate-limit storage instead of in-memory counters.
- Account-level login throttling.
- Multifactor authentication.
- Email verification and password recovery.
- Administrative activity logging.
- More comprehensive automated security testing.
- Production-grade security monitoring and database management.

## Conclusion

This assignment demonstrated the importance of reviewing and testing AI-generated code rather than assuming that generated implementations are secure.

ChatGPT produced a functional starting application with several appropriate security controls, including Argon2id password hashing, server-side sessions, and backend role enforcement.

However, the original application lacked login rate limiting and contained a Content Security Policy conflict that prevented the frontend styling from loading correctly. Both issues were identified during the security review and addressed.

The application was also expanded to support Neon PostgreSQL and deployed to Vercel, where the core authentication and authorization functionality was tested successfully.

The main takeaway is that AI can provide a useful starting point for application development, but developers remain responsible for reviewing its output, correcting weaknesses, and verifying that security controls work as expected.