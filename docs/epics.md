# FourSight Epics

This document outlines the high-level epics for the FourSight project. Each epic is broken down into individual story files located in the `docs/stories/` directory.

## Epic 1: User Authentication & Dashboard

**ID:** E01
**Description:** Handles user sign-up, login, and the main dashboard view where users can see metrics related to their decision analyses.

## Epic 2: Core Decision Analysis

**ID:** E02
**Description:** The main user workflow for inputting a decision query, selecting analytical frameworks, participating in an iterative Q&A session, and receiving a synthesized recommendation.

## Epic 3: Analysis History & Retry

**ID:** E03
**Description:** Allows users to view, access, and learn from their past analyses, including the ability to retry a decision with a different set of frameworks.

## Epic 4: System-Wide Non-Functional Requirements

**ID:** E04
**Description:** Houses the cross-cutting technical stories needed to address performance, security, scalability, and observability across the entire application.

## Epic 5: Backend Implementation

**ID:** E05
**Description:** Covers the complete backend architecture, including the design of the central Orchestrator Agent, the 10 specialized Framework Agents, the agent-to-agent communication protocol, and the data persistence strategy. The primary technologies used are the Python Agent Development Kit (ADK), Google Cloud Run for containerized deployment, and Google Firestore for data management.

### Stories

* **S5.1:** Core Setup & Orchestrator Foundation
* **S5.2:** Framework Agent Implementation
* **S5.3:** Full Workflow Integration & Finalization