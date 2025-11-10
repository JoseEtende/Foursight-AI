# Story 2.4: Orchestrated Q&A Session

**ID:** S2.4
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, after my frameworks are chosen, I want to participate in a Q&A session with the agents in a clear, organized layout, so that I can provide the necessary context for a high-quality analysis.

---

## Description

This story defines the "Information Sufficiency Analysis" and subsequent Q&A session. After the user starts the analysis, the Orchestrator polls the selected agents. The UI then transitions to a two-pane "Q&A Cockpit" view. The left pane (Orchestrator) provides a high-level summary, while the right pane contains a 2x2 grid of individual agent chat windows for detailed interaction.

---

## Acceptance Criteria

1. After clicking "Start Analysis," the Orchestrator must display a message indicating the "Information Sufficiency Analysis" has begun.
2. Upon completion of this analysis, the UI must split into two vertical panes: a larger main chat window on the left and a smaller window with a 2x2 grid on the right.
3. **Left Pane (Orchestrator Chat):**
    * Must display a summary from the Orchestrator starting with the message: "All agents have completed their initial analysis."
    * This summary must include a color-coded, bulleted list indicating the status of each of the four agents (e.g., "SWOT Agent: Ready", "Cost-Benefit Agent: Needs more information").
4. **Right Pane (Agent Chat Grid):**
    * Must display four color-coded chat "cards," one for each selected agent.
    * Agents that do not need more information must display a clear status message (e.g., "Ready to proceed").
    * Agents that need more information must immediately display their first question in their chat window.
5. **Q&A Interaction Flow:**
    * When a user submits an answer to an agent's question, the answer is saved by the orchestrator and the next question will appear in the same chat window.
    * This sequential process continues until the agent has asked all its questions (maximum of three).
    * Once a user answers the final question for an agent, its chat window must update to display the "Ready to proceed" status.
    * The user must be able to answer questions from any agent in any order (e.g., answer a question from Agent 1, then Agent 3, then Agent 1 again).
    * The user's answers, submitted in an agent's chat window, must be sent to the Orchestrator.
6. **Context Management (ADK Compliance):**
    * The Orchestrator must update a shared context with the new information from the user's answers.
    * This updated context must be broadcast to **all four** active agents.
7. **Completion:** Once all Q&A sessions are complete, all agents begin their final analysis.

---

## Backend Implementation

* This story is the core of the Orchestrator's `manage_interactive_qa` tool, as detailed in story S5.3.
* The Orchestrator will manage the state of the Q&A session in the `qa_state` field of the session document in Firestore.
* The Framework Agents will provide their questions and status as part of their first pass, as detailed in story S5.2.
* The Orchestrator will use the `ParallelAgent` to re-invoke the Framework Agents with the updated `shared_context` after the Q&A session is complete, as detailed in story S5.3.
