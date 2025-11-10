# Sprint 1 Plan: Core Decision Analysis (MVP)

**Sprint Goal:** To implement the end-to-end core user journey for the FourSight application. By the end of this sprint, a user must be able to submit a query, select frameworks, participate in a Q&A session, and receive a final, synthesized recommendation.

---

## Sprint Backlog (Prioritized)

This backlog is ordered by implementation priority. Each story includes developer notes that link it to the specific tasks in the `technical-spec.md` (Section 11).

### 1. Story 2.2: Framework Ranking

- **User Story:** As a user, I want the Orchestrator agent to analyze my query and rank all 10 available frameworks based on relevance, providing a score and rationale for each.
- **Developer Notes:**
  - This is the first functional slice of the Orchestrator.
  - Requires **Task 1.3** (Implement `rank_frameworks` tool) and **Task 1.4** (Create basic Orchestrator agent).
- Depends on the `frameworks` collection being populated (**Task 1.2**).

### 2. Story 2.1: Decision Analysis Page

- **User Story:** As a user, I want a dedicated page where I can input my decision query to begin an analysis.
- **Developer Notes:**
  - This is the primary frontend entry point for the core workflow.
  - The "submit" button on this page will trigger the backend logic defined in Story 2.2.
  - While this is a frontend story, it is the trigger for the entire backend workflow.

### 3. Story 2.3: Framework Selection UI

- **User Story:** As a user, after submitting my query, I want to see a clear and interactive page where I can review and customize the AI-recommended team of frameworks.
- **Developer Notes:**
  - This story's backend component involves persisting the user's final selection.
- Requires **Task 3.1** (Implement `store_user_selection` tool) and **Task 3.4** (Implement Firestore logic for the `sessions` collection).

### 4. Story 2.4: Orchestrated Q&A Session

- **User Story:** As a user, after my frameworks are chosen, I want to participate in a Q&A session with the agents in a clear, organized layout.
- **Developer Notes:**
  - This is the most complex part of the orchestration.
  - Requires the full implementation of the Framework Agents (**Phase 2, Tasks 2.1-2.4**).
  - Requires the Orchestrator to be able to invoke these agents. This involves **Task 3.2** (Configure `AgentTool`s) and **Task 3.3** (Implement `ParallelAgent` logic).
  - Requires the implementation of the `manage_interactive_qa` tool (**Task 3.1**).

### 5. Story 2.5: Final Analysis & Synthesized Recommendation

- **User Story:** As a user, once I have provided all the necessary information, I want to see the final, detailed analysis from each agent and receive a single, synthesized recommendation from the Orchestrator.
- **Developer Notes:**
  - This is the final step of the workflow.
  - Requires the re-invocation of the `ParallelAgent` with the updated context (**Task 3.3**).
  - Requires the implementation of the `synthesize_final_recommendation` tool (**Task 3.1**).
  - Requires the final update to the `sessions` and `users` collections in Firestore (**Task 3.4**).
