[ ] 1. Authentication Functional Tests:
- Successful registration with a new account.
- Successful login generating an active session or token.
- Failed login with an invalid password displays a generic error message.
- Logout successfully invalidates or removes the local credential/session.

[ ] 2. Authorization & Privilege Boundary Tests:
- Logging in as a standard User allows access to the User Dashboard.
- Logging in as a standard User and attempting to access the Admin view/endpoint returns a clean 403 Forbidden (or redirects safely).
- Logging in as an Admin grants access to both User and Admin resources.
- Attempting to access protected endpoints while logged out returns 401 Unauthorized.

[ ] 3. Input Validation & Edge Cases:
- Empty username/password submissions are rejected with client and server validation.
- Entering special characters or SQL-like syntax does not crash the server.

[ ] 4. Browser Console & Network Health:
- Browser DevTools Network tab shows proper HTTP status codes (200, 401, 403).
- DevTools Console is free of unhandled JavaScript runtime exceptions.