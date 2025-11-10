# Story 2.6: Synthesized Recommendation

**ID:** S2.6
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, I want to receive a single, synthesized recommendation from the Orchestrator agent, including a confidence score, executive summary, key supporting points, and key risks.

---

## Acceptance Criteria

1. After parallel execution is complete, the Orchestrator must synthesize the four individual agent outputs.
2. The final output screen must prominently display the synthesized recommendation.
3. The output must be structured with the following sections in order:
    - Recommendation & Confidence Score (e.g., High, Medium, Low).
    - Executive Summary.
    - Key Supporting Points.
    - Key Risks and Contradictions.
4. The screen must display the total cost of the analysis in both USD and LLM tokens.
5. The screen must feature an "Acknowledge" button.
6. The screen must feature a "Restart with Other Frameworks" button, which starts a new analysis with the original query and the 6 frameworks that were not used in the completed analysis.

---

## Backend Implementation

- This story is the core of the Orchestrator's `synthesize_final_recommendation` tool, as detailed in story S5.3.
- The final recommendation will be stored in the `final_recommendation` field of the session document in Firestore.
- The "Restart with Other Frameworks" button will create a new session in Firestore with the original query and the remaining frameworks.
