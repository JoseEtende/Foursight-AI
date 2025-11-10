# Story 1.4: Two-Tiered Top Navigation

**ID:** S1.4
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a user, I want a clear, two-tiered top navigation system, so that I can easily access all main sections of the application and my user profile.

---

## Description

This story defines the primary navigation structure for the application. It replaces the previous sidebar concept with a two-tiered header. The top tier provides access to global elements like the user profile and settings, while the second, floating tier provides navigation to the main pages of the application. This design maximizes the horizontal workspace for the user.

---

### Acceptance Criteria

1. A fixed **Main Top Bar** must be present at the top of all pages.
2. The Main Top Bar must display the "FourSight" logo and name in the **center**.
3. The Main Top Bar must display a **user profile icon** and a **settings icon** on the **far right**.
4. A **Floating Navigation Bar** must be displayed on all pages, directly below the Main Top Bar.
5. The Floating Navigation Bar must be **centered**.
6. The Floating Navigation Bar must contain distinct buttons for:
    - Dashboard
    - New Analysis
    - History
    - Framework Library
7. Clicking on any button in the Floating Navigation Bar must navigate the user to the corresponding page.
8. The button corresponding to the currently active page must be visually highlighted with a **purple background and white text**.

---

## Backend Implementation

- This is primarily a frontend story, but the user profile and settings icons will require backend integration to fetch user data, as detailed in story S5.3.
