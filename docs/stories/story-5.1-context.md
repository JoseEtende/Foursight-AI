# Story 5.1: Technical Context

**ID:** S5.1
**Epic:** E05 - Backend Implementation
**Author:** BMad Scrum Master
**Date:** 2025-11-08

---

## 1. Objective

This document provides the technical context required to implement Story 5.1, which focuses on setting up the foundational backend infrastructure for the FourSight application. This includes creating the Orchestrator service, a script to populate Firestore with framework data, and the necessary Docker configuration for deployment.

---

## 2. File Manifest

The following files are to be created or modified as part of this story:

| File Path | Purpose | Status |
| :--- | :--- | :--- |
| `services/orchestrator/` | Directory for the Orchestrator microservice. | Created |
| `scripts/setup_framework_embeddings.py` | Python script to populate the `frameworks` Firestore collection. | Created |
| `services/orchestrator/rank_frameworks.py` | Python module containing the framework ranking logic. | Created |
| `services/orchestrator/agent.py` | The main entry point for the Orchestrator agent. | Created |
| `services/orchestrator/Dockerfile` | Dockerfile for building the Orchestrator service container. | Created |
| `services/orchestrator/requirements.txt` | Python dependencies for the Orchestrator service. | **To be created** |

---

## 3. Implementation Details

### 3.1. `services/orchestrator/` Directory

This directory has been created and will house all the code and configuration for the Orchestrator microservice.

### 3.2. `scripts/setup_framework_embeddings.py`

- **Purpose:** This script is a one-time setup utility to populate the `frameworks` collection in Firestore.
- **Logic:**
    1. Initialize the Google Cloud Firestore client.
    2. Target the `frameworks` collection.
    3. Read each framework description from the markdown files located in `scripts/framework_descriptions/`.
    4. For each description, generate a vector embedding using the `google.generativeai` library.
    5. Create a new document in the `frameworks` collection for each framework, storing its name, description, and the generated embedding.
- **Dependencies:** `google-cloud-firestore`, `google-generativeai`

### 3.3. `services/orchestrator/rank_frameworks.py`

- **Purpose:** This module will contain the core logic for the Multi-Criteria Scoring Algorithm used to rank the 10 decision-making frameworks.
- **`rank_frameworks(query)` function:**
  - **Input:** A user's query string.
  - **Logic (Placeholder):** For this story, the function should return a hardcoded, ranked list of the 10 framework names. The actual scoring algorithm is not in scope.
  - **Output:** A list of strings.

### 3.4. `services/orchestrator/agent.py`

- **Purpose:** This is the main file for the Orchestrator agent.
- **Class:** `OrchestratorAgent` should inherit from the `adk.agent.LlmAgent`.
- **Tools:** The agent should have a `tools` dictionary that maps the string `"rank_frameworks"` to the `rank_frameworks` function from the `rank_frameworks.py` module.
- **Dependencies:** `adk`

### 3.5. `services/orchestrator/Dockerfile`

- **Purpose:** To containerize the Orchestrator service for deployment on Google Cloud Run.
- **Configuration:**
  - Base Image: `python:3.9-slim`
  - Dependencies: Copy and install `requirements.txt`.
  - Application Code: Copy the contents of the `services/orchestrator` directory into the container.
  - Port: Expose port `8080`.
  - Entrypoint: Use `gunicorn` to run the `agent:agent` instance.

### 3.6. `services/orchestrator/requirements.txt` (To Be Created)

- **Purpose:** To list the Python dependencies for the Orchestrator service.
- **Initial Content:**

    ```
    google-cloud-firestore
    adk
    gunicorn
    ```

---

## 4. Next Steps

1. Create the `services/orchestrator/requirements.txt` file with the content specified above.
2. The developer can then proceed with the implementation of the placeholder logic in the created files.
3. Once the code is complete, the developer should update the "Implementation Notes" section in the `docs/stories/story-5.1.md` file.
4. Finally, the developer will move the story status from `in-progress` to `review`.

---

## 5. Developer Guidance

**CRITICAL: It is required that you follow these guidelines to ensure a successful implementation.**

1. **Multi-Agent System Design:**
    - Before writing any code, you **must** thoroughly review the `docs/llms-full.txt` document. This file contains the complete documentation for the Python Agent Development Kit (ADK) and is the primary source of truth for designing and building multi-agent systems.
    - Pay close attention to the sections on `LlmAgent`, `BaseAgent`, and the patterns for creating multi-agent hierarchies.

2. **Interacting with Google Cloud Services:**
    - You **must** use the MCP tools to get the correct and up-to-date information on how to communicate with all Google Cloud services. This includes, but is not limited to:
        - **Firestore:** For all database operations (reading, writing, querying).
        - **Firebase Authentication:** For any user authentication logic.
        - **Google Generative AI (for Embeddings):** For generating vector embeddings.
    - Do not rely only on external documentation or web searches, as the MCP tools provide the most accurate and contextually relevant information for this project.
    - Specifically, you can use tools like `Context7` to get documentation and code samples for these services.
