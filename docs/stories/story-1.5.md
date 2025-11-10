# Story 1.5: Settings Page

**ID:** S1.5
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a user, I want a settings page so that I can manage my account details and application preferences.

---

## Description

This story covers the creation of the Settings page. Access to this page is a global element, available from the main top bar, ensuring the user can always reach their account and application settings.

---

### Acceptance Criteria

1. A "Settings" page must be accessible by clicking the **settings icon** in the main top bar.
2. The page must have a clear title: "Settings".
3. For the MVP, this page can be a placeholder, but it must be functional to navigate to.
4. The page is the designated location for future functionality, such as profile management, notification preferences, and other user-specific settings.

---

## Backend Implementation

- While the frontend is a placeholder, the backend will need to be prepared to store and retrieve user settings from the `users` collection in Firestore, as detailed in story S5.3.
