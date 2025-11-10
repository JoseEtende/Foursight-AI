# Story 2.7: Agent-Level Drill-Down

**ID:** S2.7
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, I want to be able to view the detailed, individual analysis from each of the four framework agents.

---

## Acceptance Criteria

1. On the final recommendation screen, there must be a clear way (e.g., tabs, expandable sections) to view the output from each of the four agents.
2. Each agent's section should contain its full, un-synthesized analysis and conclusion.

---

## Backend Implementation

* The individual agent reports will be fetched from the `agent_reports` field of the session document in Firestore, as detailed in story S5.3.
* The backend will need to provide an endpoint to retrieve the full session data, including the agent reports.
