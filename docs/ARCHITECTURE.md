# FourSight Architecture

**Version:** 2.0
**Date:** 2025-11-07
**Author:** BMad Architect

---

## 1. System Overview

FourSight is a multi-agent decision analysis platform built on a modern, serverless Google Cloud architecture. It is designed for scalability, modularity, and maintainability.

- **Frontend:** A Next.js/React application provides the user interface.
- **Backend:** The backend consists of multiple Python services built with the **Agent Development Kit (ADK)**. Each service is containerized and deployed independently on **Google Cloud Run**.
- **Core Logic:** A central **Orchestrator Agent** manages the entire decision workflow. It invokes four user-selected **Framework Agents** in parallel to perform specialized analysis.
- **Data Persistence:** All application data, session state, and user history are stored in **Google Firestore**.
- **Authentication:** User identity is managed by **Firebase Authentication**.

---

## 2. Core Architectural Decisions

| Category | Decision | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | Python ADK | The mandated toolkit for building scalable, interoperable AI agents. |
| **Deployment Target** | Google Cloud Run | Serverless, container-based platform that provides automatic scaling (including to zero), isolation, and simplified management for our microservices-based agent architecture. |
| **Database** | Google Firestore | NoSQL, serverless database that integrates seamlessly with Cloud Run and Firebase Auth. Its document model is a perfect fit for storing structured session state and user data. |
| **Agent Communication** | Direct Invocation via `ParallelAgent` | The ADK's `ParallelAgent` provides a robust, built-in mechanism for concurrent agent execution. This simplifies the architecture by removing the need for an external messaging bus (like Pub/Sub) for core agent-to-agent calls. |
| **Authentication** | Firebase Authentication | Provides a secure, easy-to-use authentication system that integrates directly with our chosen database (Firestore) and frontend framework. |
| **CI/CD Pipeline** | Google Cloud Build | A fully managed CI/CD platform to automate the building, testing, and deployment of our containerized agent services to Cloud Run. |

---

## 3. High-Level Workflow & Components

The system's workflow is managed entirely by the Orchestrator Agent and follows a two-pass analysis model.

```
+---------------------------------------------------------------------------------+
|                                  FourSight System                               |
|                                                                                 |
|  [User] <=> [Frontend (Next.js on Cloud Run)] <=> [Orchestrator (ADK on Cloud Run)] |
|                                                              |                  |
|                                                              | (Invokes via)    |
|                                                              v                  |
|                                     +--------------------------+                |
|                                     |  ADK ParallelAgent       |                |
|                                     +--+--------------------+--+                |
|                                        |                    |                   |
|              +-------------------------+--------------------+-------------------+
|              |                         |                    |                   |
|              v                         v                    v                   v
|  +-----------------------+  +--------------------+  +-------------------+  +-------------------+
|  | Framework Agent 1     |  | Framework Agent 2  |  | Framework Agent 3 |  | Framework Agent 4 |
|  | (ADK on Cloud Run)    |  | (ADK on Cloud Run) |  | (ADK on Cloud Run)|  | (ADK on Cloud Run)|
|  +-----------------------+  +--------------------+  +-------------------+  +-------------------+
|                                                                                 |
+---------------------------------------------------------------------------------+
```

1. **Query & Rank:** The user submits a query. The **Orchestrator** uses a Multi-Criteria Scoring Algorithm (including vector embedding similarity) to rank 10 frameworks.
2. **Selection:** The user selects four frameworks.
3. **Pass 1 (Parallel Invocation):** The Orchestrator uses a **`ParallelAgent`** to invoke the four selected **Framework Agents** concurrently for an "Information Sufficiency Analysis."
4. **Q&A (If Needed):** If any agents return questions, the Orchestrator manages an interactive Q&A session with the user.
5. **Pass 2 (Parallel Invocation):** The Orchestrator re-invokes the four agents via the **`ParallelAgent`**, providing the full context (query + answers).
6. **Synthesis:** The Orchestrator receives the four final reports and synthesizes them into a single, actionable recommendation.

---

## 4. Data Model (Firestore)

The database is structured into three top-level collections, optimizing for performance and data integrity.

### 4.1. `frameworks` Collection

Stores static, pre-computed data for the 10 decision frameworks. Populated once by a setup script.

- **Purpose:** Enables efficient semantic ranking and provides a single source of truth for framework knowledge.
- **Structure:** `{ name, description, embedding }`

### 4.2. `users` Collection

Maintains a denormalized, read-optimized list of all analyses a user has initiated.

- **Purpose:** Powers the rich user history view, allowing users to see key outcomes at a glance.
- **Structure:** `{ user_id, sessions: [ { session_id, query, recommendation, confidence, cost_usd, created_at, status } ] }`

### 4.3. `sessions` Collection

Stores the complete, real-time state for every individual decision workflow. This is the single source of truth for an active or completed analysis.

- **Purpose:** To serve as the comprehensive state record for a single workflow.
- **Structure:** `{ session_id, user_id, query, ranked_frameworks, selected_frameworks, qa_state, agent_reports, final_recommendation, cost_usd, ... }`

---

## 5. Agent Implementation Strategy

- **Orchestrator Agent:** A stateful `LlmAgent` with a suite of tools (`rank_frameworks`, `invoke_framework_agents`, etc.) that contain the core business logic.
- **Framework Agents:** Stateless, tool-less `LlmAgent` instances. Their behavior is dictated by a composite prompt that combines operational instructions (the two-pass logic) with their specific knowledge base (the full framework description loaded from a file).

This architecture ensures a clean separation of concerns, high cohesion, and low coupling between system components.
