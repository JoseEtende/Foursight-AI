# Story 3.2: Retry with Other Frameworks

**ID:** S3.2
**Epic:** E03 - Analysis History & Retry
**User Story:** As a user, I want to be able to retry a past analysis with the 6 frameworks that were not used in the original analysis.

---

## Acceptance Criteria

1. Each card on the history page must have a "Retry" button or link.
2. Clicking "Retry" starts a new analysis workflow.
3. The new analysis must be pre-populated with the original decision query.
4. The user is taken to the framework selection screen.
5. On this screen, only the six frameworks that were *not* used in the original analysis are available for ranking and selection.

---

## Backend Implementation

* Clicking the "Retry" button will create a new session in Firestore with the original query and the remaining frameworks.
* The Orchestrator will then initiate the `rank_frameworks` tool with the subset of 6 frameworks, as detailed in story S5.1.
