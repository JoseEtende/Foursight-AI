# Technical Specification: Epic E05 - Backend Implementation

**Version:** 1.0
**Date:** 2025-11-08
**Author:** BMad Scrum Master

## 1. Overview and Scope

This document outlines the technical specification for the backend implementation of the FourSight project, as defined in Epic E05. The backend is a multi-agent system built on a serverless Google Cloud architecture, utilizing the Python Agent Development Kit (ADK) for agent creation, Google Cloud Run for deployment, and Google Firestore for data persistence. The core of the backend is the Orchestrator Agent, which manages the decision analysis workflow and coordinates with specialized Framework Agents.

### 1.1. Objectives & Scope

**In Scope:**

* Implementation of the central Orchestrator Agent.
* Implementation of the 10 specialized Framework Agents.
* Definition and implementation of the agent-to-agent (A2A) communication protocol.
* Design and implementation of the Firestore data model for storing user data, session state, and framework information.
* Deployment of all backend services as containerized applications on Google Cloud Run.

**Out of Scope:**

* Frontend application development.
* User authentication implementation (covered in Epic E01).
* CI/CD pipeline setup.

### 1.2. System Architecture Alignment

The backend implementation will adhere strictly to the architecture defined in the FourSight Architecture document. The system will be composed of containerized microservices running on Google Cloud Run, with a central Orchestrator Agent managing the workflow and communicating with Framework Agents via the ADK's `ParallelAgent`. Data will be stored in Google Firestore, following the defined data model.

## 2. Detailed Design

### 2.1. Services and Modules

| Service/Module | Responsibilities | Inputs/Outputs | Owner |
| :--- | :--- | :--- | :--- |
| **Orchestrator Agent** | Manages the end-to-end decision analysis workflow, including framework ranking, agent invocation, Q&A sessions, and final synthesis. | **Inputs:** User query. **Outputs:** Synthesized recommendation. | Backend Team |
| **Framework Agents (x10)** | Perform specialized analysis based on their assigned decision-making framework. | **Inputs:** User query, shared context. **Outputs:** Analysis report. | Backend Team |

### 2.2. Data Models

The backend will utilize the following Firestore collections:

* **`frameworks`**: Stores static data for the 10 decision frameworks.
  * `name`: string
  * `description`: string
  * `embedding`: array
* **`users`**: Stores a denormalized list of user analyses.
  * `user_id`: string
  * `sessions`: array of maps
    * `session_id`: string
    * `query`: string
    * `recommendation`: string
    * `confidence`: string
    * `cost_usd`: number
    * `created_at`: timestamp
    * `status`: string
* **`sessions`**: Stores the complete state for each decision workflow.
  * `session_id`: string
  * `user_id`: string
  * `query`: string
  * `ranked_frameworks`: array of maps
  * `selected_frameworks`: array of strings
  * `qa_state`: map
  * `agent_reports`: map
  * `final_recommendation`: map
  * `cost_usd`: number

### 2.3. APIs and Interfaces

Internal communication between the Orchestrator and Framework Agents will be handled by the Python ADK's `ParallelAgent`. No external APIs will be exposed by the Framework Agents. The Orchestrator will expose a single API endpoint for the frontend to initiate and manage the decision analysis workflow.

### 2.4. Workflows and Sequencing

The backend workflow is as follows:

1. The frontend sends the user's query to the Orchestrator Agent.
2. The Orchestrator ranks the 10 frameworks and returns the ranking to the frontend.
3. The frontend sends the user's selected four frameworks to the Orchestrator.
4. The Orchestrator invokes the four selected Framework Agents in parallel for the Information Sufficiency Analysis.
5. If any agents have questions, the Orchestrator manages the Q&A session with the user via the frontend.
6. The Orchestrator re-invokes the four agents in parallel with the full context.
7. The Orchestrator receives the final reports from the agents and synthesizes them into a single recommendation.
8. The Orchestrator returns the final recommendation to the frontend.

## 3. Non-Functional Requirements

### 3.1. Performance

The parallel execution of Framework Agents should be optimized to minimize user wait times. The Orchestrator should be able to handle multiple concurrent analysis sessions.

### 3.2. Security

All communication between the frontend and the Orchestrator will be over HTTPS. Secrets will be managed using Google Secret Manager.

### 3.3. Reliability

The serverless architecture on Google Cloud Run will provide high availability and automatic scaling.

### 3.4. Observability

All backend services will have centralized logging and monitoring to track performance, errors, and LLM token usage.

## 4. Dependencies and Integrations

The backend services will have the following dependencies:

* **Python ADK:** For building the Orchestrator and Framework Agents.
* **Google Cloud Run:** For deploying the containerized backend services.
* **Google Firestore:** For data persistence.
* **Firebase Authentication:** For user authentication.
* **Google Secret Manager:** For managing secrets.

## 5. Acceptance Criteria and Traceability

### 5.1. Acceptance Criteria

* The Orchestrator Agent can successfully rank the 10 frameworks based on a user's query.
* The Orchestrator Agent can successfully invoke four selected Framework Agents in parallel.
* The Framework Agents can successfully perform their analysis and return a report.
* The Orchestrator Agent can successfully manage a Q&A session between the user and the Framework Agents.
* The Orchestrator Agent can successfully synthesize the four agent reports into a single recommendation.
* All backend services can be successfully deployed to Google Cloud Run.
* All user data, session state, and framework information is correctly stored in and retrieved from Google Firestore.

### 5.2. Traceability Mapping

| Acceptance Criteria | Spec Section(s) | Component(s)/API(s) | Test Idea |
| :--- | :--- | :--- | :--- |
| Orchestrator can rank frameworks | 2.4 | Orchestrator Agent | Unit test the ranking algorithm. |
| Orchestrator can invoke agents | 2.4 | Orchestrator Agent, `ParallelAgent` | Integration test the invocation of mock Framework Agents. |
| Agents can perform analysis | 2.1 | Framework Agents | Unit test each Framework Agent with a sample query. |
| Orchestrator can manage Q&A | 2.4 | Orchestrator Agent | Integration test the Q&A workflow with mock agents and user input. |
| Orchestrator can synthesize reports | 2.4 | Orchestrator Agent | Unit test the synthesis logic with sample agent reports. |
| Services can be deployed | 2.1 | All services | End-to-end test the deployment to a staging environment. |
| Data is stored correctly | 2.2 | All services, Firestore | Integration test the data persistence and retrieval. |

## 6. Risks, Assumptions, and Test Strategy

### 6.1. Risks, Assumptions, and Questions

* **Risk:** The Python ADK is a new technology, and there may be unforeseen challenges in its implementation.
* **Assumption:** The Google Cloud services will be available and perform as expected.
* **Question:** What is the expected load on the system, and how will it affect the performance and cost of the serverless architecture?

### 6.2. Test Strategy

The backend will be tested at three levels:

* **Unit tests:** Each agent and module will have a comprehensive suite of unit tests.
* **Integration tests:** The interaction between the Orchestrator and Framework Agents, as well as the interaction with Firestore, will be tested.
* **End-to-end tests:** The entire backend workflow will be tested from the API endpoint to the final recommendation.
