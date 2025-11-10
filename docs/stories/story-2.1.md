# Story 2.1: Decision Analysis Page

**ID:** S2.1
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, I want a dedicated page where I can input my decision query to begin an analysis.

---

## Acceptance Criteria

1. There must be a dedicated "New Analysis" page, separate from the dashboard.
2. The page must have a prominent header with a title (e.g., "What decision are you facing?") and a subtitle explaining the purpose of the page.
3. The page must feature a prominent text input field for the user's query.
4. The text input field must contain helpful placeholder text (e.g., "Should I expand my business into a new market?...").
5. Instructional helper text must be present below the input field to guide the user (e.g., "Be as detailed as possible...").
6. Below the input field, a 2x2 grid of cards must display four example queries.
7. Clicking on an example query card must populate the main text input field with that query's text.
8. The interface must include a button to submit the query and proceed to the framework selection step.
9. The text field should be large enough to accommodate multi-sentence queries.
10. This page must be accessed by clicking the **"+ New Analysis"** button in the floating navigation bar.

---

## Backend Implementation

* Submitting the query will initiate the backend workflow, starting with the Orchestrator's `rank_frameworks` tool, as detailed in story S5.1.
* A new session document will be created in the `sessions` collection in Firestore to store the state of the analysis, as detailed in story S5.3.
