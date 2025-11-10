# Story 1.2: User Login

**ID:** S1.2
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a registered user, I want to be able to log in to the application using my email and password, so that I can access my dashboard.

---

## Acceptance Criteria

1. A login form must be available to unauthenticated users.
2. The form must require a registered email address and the correct password.
3. Password entry must be masked.
4. Upon successful login, the user is redirected to their dashboard.
5. The system must display an error message for invalid credentials.

---

## Backend Implementation

* This story depends on the completion of the backend user authentication system, which is tracked in story S5.1.
* User login will authenticate against the user document in the `users` collection in Firestore, as detailed in story S5.3.
