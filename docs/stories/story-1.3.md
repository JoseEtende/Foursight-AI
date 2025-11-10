# Story 1.3: User Dashboard

**ID:** S1.3
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a logged-in user, I want to see a dashboard that displays my key metrics related to my decision analysis history.

---

## Acceptance Criteria

1. The dashboard must be the default view for authenticated users.
2. The dashboard must display the following metrics, clearly labeled:
    - Total decisions analyzed (as an integer).
    - Average confidence level (e.g., "High", "Medium", "Low").
    - A chart (e.g., bar chart) showing the frequency of use for each framework.
    - Total LLM costs, formatted as dollars (e.g., "$1.23").
3. The data must be specific to the logged-in user.

---

## Backend Implementation

- The dashboard will be populated with data from the user's `sessions` array in the `users` collection in Firestore, as detailed in story S5.3.
- The backend will need to provide an endpoint that aggregates the required metrics from the user's session data.
