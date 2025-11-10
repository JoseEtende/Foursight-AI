# Story 2.5: Final Analysis & Synthesized Recommendation

**ID:** S2.5
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, once I have provided all the necessary information, I want to see the final, detailed analysis from each agent and receive a single, synthesized recommendation from the Orchestrator.

---

## Description

This is the final step of the core workflow. After the Q&A session is complete, the Orchestrator re-invokes all four agents with the complete context. The agents perform their final analysis, and the Orchestrator synthesizes their reports into a single, actionable recommendation for the user.

---

## Acceptance Criteria

1. **GIVEN** the user has answered the final question in the Q&A session,
    **WHEN** all agents are in the "Ready to proceed" state,
    **THEN** the Orchestrator chat (left pane) must display a message indicating that the final analysis has begun (e.g., "Thank you. All agents now have the information they need. The final analysis is underway.").
2. **GIVEN** the final analysis is running,
    **WHEN** an individual Framework Agent completes its work,
    **THEN** its corresponding card in the 2x2 grid (right pane) must update to display its full, final report.
3. **GIVEN** an agent's final report is displayed,
    **WHEN** the user inspects it,
    **THEN** it must contain all the key components of its analysis (e.g., for SWOT: Strengths, Weaknesses, etc.) and must include a `caveat` if the agent still lacked critical information.
4. **GIVEN** all four agents have completed their final analysis,
    **WHEN** all four cards in the 2x2 grid are displaying their final reports,
    **THEN** the Orchestrator chat (left pane) must display the final, synthesized recommendation.
5. **GIVEN** the final recommendation is displayed,
    **WHEN** the user reads it,
    **THEN** it must contain a clear `recommendation`, a detailed `rationale` explaining how the conclusion was reached, and a consolidated list of all `caveats` from the individual agents.

---

## Backend Implementation

* This story is the core of the Orchestrator's `synthesize_final_recommendation` tool, as detailed in story S5.3.
* The Framework Agents will provide their final analysis reports as part of their second pass, as detailed in story S5.2.
* The final recommendation and agent reports will be stored in the `final_recommendation` and `agent_reports` fields of the session document in Firestore, as detailed in story S5.3.
