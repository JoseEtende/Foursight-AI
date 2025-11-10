# Story 1.1: User Registration

**ID:** S1.1
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a new user, I want to be able to register for an account using my email and a password, so that I can access the application.

---

## Acceptance Criteria

1. A registration form must be available to unauthenticated users.
2. The form must require a valid email address and a password.
3. Password entry must be masked.
4. Upon successful registration, the user is automatically logged in and redirected to their dashboard.
5. The system must handle cases where the email address is already registered.

---

### Backend Implementation

* This story depends on the completion of the backend user authentication system, which is tracked in story S5.1.
* User registration will create a new user document in the `users` collection in Firestore, as detailed in story S5.3.
