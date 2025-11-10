# Story 1.7: Safeguard for Ongoing Analysis

**ID:** S1.7
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a user, when I start a new analysis while another is in progress, I want to be warned and asked for confirmation, so that I don't accidentally lose my ongoing work.

---

## Description

This story defines a critical safeguard for the user. The "+ New Analysis" button is globally accessible in the floating navigation bar. This story ensures that if a user clicks this button while a previous analysis is still running, they are presented with a clear choice rather than immediately losing their work.

---

## Acceptance Criteria

1. If no analysis is currently in progress, clicking the **"+ New Analysis"** button in the floating navigation bar navigates the user directly to the "New Analysis" page.
2. If an analysis *is* currently running, clicking the **"+ New Analysis"** button must trigger a confirmation modal.
3. The confirmation modal must display a clear warning message (e.g., "An analysis is already in progress. Starting a new one will terminate the current analysis.").
4. The modal must provide two distinct options:
    - A **"Cancel"** button that closes the modal and allows the current analysis to continue.
    - A **"Terminate & Start New"** button that stops the ongoing analysis and navigates the user to the "New Analysis" page.

---

## Backend Implementation

- The frontend will need to query the backend to check the status of the user's most recent session in the `sessions` collection in Firestore, as detailed in story S5.3.
- If the user chooses to terminate the ongoing analysis, the frontend will need to send a request to the backend to update the status of the session to "terminated".
