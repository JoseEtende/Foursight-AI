# Story 3.1: Analysis History Page

**ID:** S3.1
**Epic:** E03 - Analysis History & Retry
**User Story:** As a user, I want to view a history page that displays a detailed, scrollable grid of all my past decision analyses.

---

## Description

This story defines the "History" page, which allows users to review their past work. The page will feature a two-column grid of interactive cards, with each card providing a comprehensive summary of a completed analysis. The design must be clean, data-rich, and consistent with the application's overall theme.

---

## Acceptance Criteria

1. The application must have a "History" page accessible by clicking the **"History"** button in the floating navigation bar.
2. The page must display past analyses in a **scrollable, two-column grid**.
3. The grid must be sorted chronologically, with the most recent analysis appearing at the top-left.
4. Each analysis must be represented as a card, styled according to the application's **"Modern Layered Design"** theme.
5. Each card must display the following information:
    * The original **decision query**.
    * The final **recommendation**.
    * The **confidence level** (e.g., "High Confidence"), displayed as a styled tag.
    * The **date** of the analysis.
    * The total **cost** of the analysis.
    * The four **frameworks used**, displayed as styled tags.
    * A button labeled **"Retry with Other Frameworks"**.

---

## Backend Implementation

* The data for the history page will be fetched from the user's `sessions` array in the `users` collection in Firestore, as detailed in story S5.3.
* The backend will need to provide an endpoint to retrieve all of the user's past sessions.
