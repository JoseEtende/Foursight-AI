# Story 2.8: Explicit Information Gaps

**ID:** S2.8
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, if an agent performs its analysis with incomplete data, I want its final report to include a clear statement identifying the missing information and explaining how this gap could potentially affect the outcome.

---

## Acceptance Criteria

1. If an agent proceeds with an analysis after exhausting its question limit without sufficient data, its final report must be flagged.
2. The agent's individual drill-down report (from Story 2.7) must contain a dedicated section titled "Information Gaps".
3. This section must list the specific information the agent was missing and provide a brief explanation of how that missing data might have altered the analysis.

---

## Backend Implementation

* The `caveat` field in the Framework Agent's final JSON report will be used to populate the "Information Gaps" section, as detailed in story S5.2.
* The Orchestrator will store this information in the `agent_reports` field of the session document in Firestore, as detailed in story S5.3.
