# Technical Specification: FourSight Multi-Agent System

**Version:** 1.4
**Date:** 2025-11-06
**Author:** BMad Product Manager

---

## 1. Introduction

### 1.1. Purpose

This document provides a comprehensive technical specification for the development of the **FourSight** system. FourSight is a multi-agent decision analysis platform designed to assist users in making complex decisions by leveraging a suite of specialized AI agents, each an expert in a specific decision-making framework.

### 1.2. Scope

This specification covers the complete backend architecture, including the design of the central **Orchestrator Agent**, the 10 specialized **Framework Agents**, the agent-to-agent communication protocol, and the data persistence strategy. The primary technologies used are the Python Agent Development Kit (ADK), Google Cloud Run for containerized deployment, and Google Firestore for data management.

### 1.3. System Overview

The system is architected around a central Orchestrator that manages the user interaction and workflow. Based on a user's query, it intelligently ranks 10 decision-making frameworks. The user selects four of these frameworks, and the Orchestrator coordinates with the corresponding agents to perform a multi-stage analysis, including an information-gathering Q&A session, before synthesizing a final recommendation.

---

## 2. Agent Design Philosophy

### 2.1. Centralized Orchestration

The system's stability and predictability rely on a single **Orchestrator Agent** that manages the state and flow of the entire process. Framework Agents do not communicate with each other directly; all interactions are mediated by the Orchestrator, preventing chaotic behavior and ensuring a structured workflow.

### 2.2. Specialization and Expertise

Each of the 10 **Framework Agents** is designed as a domain expert. Its prompt, description, and internal logic are narrowly focused on executing its specific framework. This specialization ensures high-quality, focused analysis from each agent.

### 2.3. Autonomy with Guardrails

While agents are autonomous in their analysis, they operate within strict procedural guardrails defined by the Orchestrator's instructions. The **Information Sufficiency Analysis** is a key mechanism that provides agents with the autonomy to request more information while ensuring the overall process remains on track.

### 2.4. Scalability and Modularity

The architecture is designed to be modular. Each agent is a self-contained service, allowing for independent development, deployment, and scaling. New framework agents can be added to the system with minimal changes to the core orchestration logic.

---

## 3. System Workflows

### 3.1. Orchestrator Workflow

From the Orchestrator's point of view, the process is a stateful, user-centric sequence of events:

1. **Receive & Rank:** The Orchestrator receives the user's initial decision query. It immediately uses its `rank_frameworks` tool, which employs an enhanced **Multi-Criteria Scoring Algorithm**, to score and rank the 10 available decision frameworks. This algorithm evaluates frameworks against a set of weighted criteria, including semantic relevance, complexity match, and data availability, to produce a transparent and auditable score (see Section 4.1.1 for details).
2. **Present & Await Selection:** It presents the ranked list to the user, with the top 4 highlighted, and waits for the user to validate or customize their selection of four frameworks.
3. **Store Selection:** Once the user confirms their final four frameworks, the Orchestrator saves this selection into the session state.
4. **Initiate Analysis (Parallel Invocation):** The Orchestrator invokes the four corresponding Framework Agents in parallel. It passes each agent the user's original query.
5. **Manage Interactive Q&A Round:**
    * It gathers the initial status payloads from all four agents.
    * It informs the user which agents are ready and which require more information.
    * For each agent needing information, the Orchestrator facilitates an interactive Q&A session:
        * It displays the *first* question from an agent in that agent's UI card.
        * When the user answers, it displays the *next* question for that agent, until all of that agent's questions (max 3) have been answered.
        * This happens in parallel for all agents that need information; the user can answer questions in any order.
    * The Orchestrator waits until **all questions from all agents** have been answered.
6. **Update Shared Context:** Once the Q&A round is fully complete, the Orchestrator consolidates all the user's answers and updates the `shared_context` in the session state.
7. **Trigger Final Analysis:** It re-invokes all four selected agents in parallel, this time passing the complete, updated `shared_context`.
8. **Synthesize & Recommend:** With the final, detailed analyses from all four agents, the Orchestrator's final prompt instructs it to synthesize these diverse outputs—including any caveats—into a single, comprehensive recommendation.
9. **Deliver Final Report:** The Orchestrator presents this synthesized recommendation to the user, concluding the workflow.

### 3.2. Framework Agent Workflow

From the perspective of any individual Framework Agent, the process is a stateless, two-pass execution managed by the Orchestrator. Each agent is an `LlmAgent` whose behavior is guided by its detailed instructional prompt.

#### 3.2.1. First Pass: Information Sufficiency Analysis

1. **Activation:** The agent is invoked by the Orchestrator, receiving only the user's `original_query`.
2. **Internal Analysis:** The agent's LLM analyzes the query against its comprehensive framework knowledge to answer the question: "Do I have enough information to perform a complete analysis?"
3. **First Pass Response:** The agent returns a single JSON object to the Orchestrator with one of two structures:
    * **If information is sufficient:**

        ```json
        {
          "status": "sufficient",
          "questions": []
        }
        ```

    * **If information is insufficient:** The agent generates up to 3 critical questions.

        ```json
        {
          "status": "insufficient",
          "questions": ["Question 1?", "Question 2?", "Question 3?"]
        }
        ```

4. **Termination:** The agent's instance terminates.

#### 3.2.2. Second Pass: Final Analysis

1. **Re-activation:** The agent is invoked a second time by the Orchestrator, receiving the full `shared_context` (original query + all Q&A answers).
2. **Final Analysis Execution:** The agent performs its complete analysis using its specific framework.
    * **No More Questions:** The agent is explicitly prohibited from asking for more information in this phase.
    * **Caveat Generation:** If the agent's LLM determines that critical information is *still* missing, it MUST generate a `caveat` string explaining the gap and its impact on the analysis.
3. **Final Report Generation:** The agent generates its final analysis in a structured JSON format specific to its framework (e.g., for SWOT, this would include `strengths`, `weaknesses`, etc.). The `caveat` field must be included if one was generated.
4. **Termination:** After returning its final JSON report, the agent's instance terminates. It retains no memory or state.

---

## 4. Orchestrator Agent Implementation

The Orchestrator Agent is the central component of the FourSight system. Below is a conceptual implementation based on the official structure of the Python ADK.

### 4.1. Agent Definition (`agent.py`)

The agent is defined using the `Agent` class, which includes its instructional prompt, a descriptive name, and the tools it can invoke.

```python
# services/orchestrator/app/agent.py

from adk.agent import LlmAgent
from adk.tools import tool, AgentTool
from . import tools

# ... (AgentTool definitions for all 10 framework agents)

# The Orchestrator's instructional prompt
ORCHESTRATOR_PROMPT = """..."""

def get_agent():
    """Builds and returns the Orchestrator Agent."""
    return LlmAgent(
        prompt=ORCHESTRATOR_PROMPT,
        description="The central orchestrator for the FourSight decision analysis system.",
        tools=[
            tools.rank_frameworks,
            tools.store_user_selections,
            tools.post_ui_message,
            # ... (add all other framework agent tools here)
        ]
    )


```

#### 4.1.1. Framework Ranking Algorithm

The `rank_frameworks` tool implements an enhanced Multi-Criteria Scoring Algorithm to ensure a robust, transparent, and accurate ranking of decision frameworks. This method combines semantic relevance with a detailed analysis of the query's characteristics against each framework's strengths.

The algorithm is defined as follows:

```python
def calculate_framework_score_enhanced(framework, query_analysis, query_embedding):
    """
    Calculate suitability score (0-100) for a framework with Semantic Relevance.
    
    Criteria weights:
    - Semantic Relevance: 10%
    - Complexity Match: 20%
    - Data Availability: 15%
    - Time Sensitivity: 15%
    - Quantitative Need: 15%
    - Stakeholder Involvement: 15%
    - Strategic vs Operational: 10%
    """
    
    framework_embedding = get_precomputed_embedding(framework.name)

    criteria_scores = {
        'semantic_relevance': calculate_cosine_similarity(query_embedding, framework_embedding),
        'complexity_match': assess_complexity_match(framework, query_analysis),
        'data_availability': assess_data_availability(framework, query_analysis),
        'time_sensitivity': assess_time_sensitivity(framework, query_analysis),
        'quantitative_need': assess_quantitative_need(framework, query_analysis),
        'stakeholder_involvement': assess_stakeholder_need(framework, query_analysis),
        'strategic_operational': assess_strategic_fit(framework, query_analysis)
    }
    
    weights = {
        'semantic_relevance': 0.10,
        'complexity_match': 0.20,
        'data_availability': 0.15,
        'time_sensitivity': 0.15,
        'quantitative_need': 0.15,
        'stakeholder_involvement': 0.15,
        'strategic_operational': 0.10
    }
    
    total_score = sum(criteria_scores[k] * weights[k] for k in criteria_scores)
    
    return int(total_score * 100)  # Scale to 0-100
```

**Implementation Details:**

* **Semantic Relevance:** Calculated using cosine similarity between pre-computed vector embeddings of framework descriptions and the user's query embedding.
* **`assess_*` Functions:** Each of the other criteria is assessed by a dedicated helper function that uses an LLM to analyze the query and score the framework's suitability for that specific criterion on a scale of 0.0 to 1.0.

### 4.2. Framework Agent Implementation (`agent.py`)

Each of the 10 Framework Agents shares an identical architecture, differing only in their specific instructional content. They are designed as stateless, analysis-focused workers.

#### 4.2.1. Agent Definition and Prompt Engineering

Each Framework Agent is an `LlmAgent`. Its core instruction is a composite prompt, dynamically constructed by embedding its detailed knowledge base within an operational "wrapper" prompt. This ensures each agent knows both *what* its framework is and *how* to execute the required workflow.

**Prompt Structure:**

1. **Wrapper Prompt:** A static template that defines the agent's persona, its strict two-pass operational logic (Pass 1: Sufficiency Analysis, Pass 2: Final Analysis), and the required JSON output formats for each pass.
2. **Knowledge Base:** The full, multi-section content loaded directly from the agent's corresponding markdown file in `scripts/framework_descriptions/`.

**Conceptual Implementation (`pros_cons` agent):**

```python
# services/framework-agent-pros-cons/app/agent.py

from adk.agent import LlmAgent
import os

def load_knowledge_base():
    """Loads the full knowledge base from the markdown file."""
    path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts', 'framework_descriptions', 'pros_cons.md')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# The operational wrapper prompt that gives the agent its commands

PROMPT_TEMPLATE = """
You are an expert AI agent specializing in the **Pros and Cons Analysis** framework.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles.

---

<knowledge_base>
{framework_description}
</knowledge_base>

---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single JSON object.

**PASS 1: Information Sufficiency Analysis**
If you receive only an `original_query`, your task is to determine if you have enough information to perform a complete Pros and Cons analysis.
- If YES, you MUST return the following JSON object:
  `{{"status": "sufficient", "questions": []}}`
- If NO, you MUST generate up to 3 critical questions to gather the necessary information and return the following JSON object:
  `{{"status": "insufficient", "questions": ["Question 1?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
If you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis.
- You are PROHIBITED from asking more questions.
- Use all available information (the original query and all answers) to conduct the most thorough analysis possible.
- If you determine that critical information is still missing, you MUST generate a `caveat` field in your final report explaining the gap and its impact.
- Your final output MUST be a JSON object containing the full analysis, like this:
  `{{"pros": ["...", "..."], "cons": ["...", "..."], "recommendation": "...", "caveat": "..."}}`
"""

def get_agent():
    """Builds and returns the Pros and Cons Framework Agent."""
    
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    
    return LlmAgent(
        prompt=final_prompt,
        description="A specialized agent for performing a Pros and Cons analysis.",
        tools=[]  # Framework agents have no tools
    )
```

### 4.2. ADK Entrypoint & Serving

The ADK provides a command-line interface for running agents. There is no need for a custom entrypoint script. Each agent service will be started from the command line within its container.

**To run an agent locally for testing:**

```bash
# Navigate to the service directory
cd services/orchestrator

# Run the agent's web server
adk web --port 8080
```

The `Dockerfile` for each service will be configured to use this command as its entrypoint, ensuring the agent is served correctly when deployed to Google Cloud Run.

---

## 5. Framework Agent Implementation

Each of the 10 Framework Agents shares an identical architecture, differing only in their specific instructional content. They are designed as stateless, analysis-focused workers.

### 5.1. Agent Definition and Prompt Engineering

Each Framework Agent is an `LlmAgent`. Its core instruction is a composite prompt, dynamically constructed by embedding its detailed knowledge base within an operational "wrapper" prompt. This ensures each agent knows both *what* its framework is and *how* to execute the required workflow.

**Prompt Structure:**

1. **Wrapper Prompt:** A static template that defines the agent's persona, its strict two-pass operational logic (Pass 1: Sufficiency Analysis, Pass 2: Final Analysis), and the required JSON output formats for each pass.
2. **Knowledge Base:** The full, multi-section content loaded directly from the agent's corresponding markdown file in `scripts/framework_descriptions/`.

**Conceptual Implementation (`pros_cons` agent):**

``` python
# services/framework-agent-pros-cons/app/agent.py

from adk.agent import LlmAgent
import os

def load_knowledge_base():
    """Loads the full knowledge base from the markdown file."""
    path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts', 'framework_descriptions', 'pros_cons.md')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# The operational wrapper prompt that gives the agent its commands
PROMPT_TEMPLATE = """
You are an expert AI agent specializing in the **Pros and Cons Analysis** framework.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles.

---

<knowledge_base>
{framework_description}
</knowledge_base>

---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single JSON object.

**PASS 1: Information Sufficiency Analysis**
If you receive only an `original_query`, your task is to determine if you have enough information to perform a complete Pros and Cons analysis.
- If YES, you MUST return the following JSON object:
  `{{"status": "sufficient", "questions": []}}`
- If NO, you MUST generate up to 3 critical questions to gather the necessary information and return the following JSON object:
  `{{"status": "insufficient", "questions": ["Question 1?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
If you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis.
- You are PROHIBITED from asking more questions.
- Use all available information (the original query and all answers) to conduct the most thorough analysis possible.
- If you determine that critical information is still missing, you MUST generate a `caveat` field in your final report explaining the gap and its impact.
- Your final output MUST be a JSON object containing the full analysis, like this:
  `{{"pros": ["...", "..."], "cons": ["...", "..."], "recommendation": "...", "caveat": "..."}}`
"""

def get_agent():
    """Builds and returns the Pros and Cons Framework Agent."""
    
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    
    return LlmAgent(
        prompt=final_prompt,
        description="A specialized agent for performing a Pros and Cons analysis.",
        tools=[]  # Framework agents have no tools
    )
```

---

## 6. File Structure and Containerization

### 6.1. Monorepo Service Structure

The project will be organized as a monorepo with a `services` directory. Each agent (the Orchestrator and all 10 Framework Agents) will have its own dedicated subdirectory, ensuring clear separation of concerns.

```
/
├── services/
│   ├── orchestrator/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py      # LlmAgent definition
│   │   │   └── tools.py      # Orchestrator's business logic
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── framework-agent-pros-cons/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   └── agent.py      # LlmAgent definition for this framework
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── ... (10 more framework agent service directories)
│
├── firebase.json
└── firestore.rules
```

### 6.2. Containerization with Docker

Each service in the monorepo will have its own `Dockerfile`. This allows each agent to have its own specific dependencies (e.g., `sentence-transformers` for the Orchestrator) without bloating other services. The Dockerfiles will be configured to build a production-ready container image for each agent.

### 6.3. Deployment on Google Cloud Run

Each agent's container image will be deployed as a separate, independent service on Google Cloud Run. This serverless architecture provides:

* **Automatic Scaling:** Services will scale up or down (even to zero) based on request volume.
* **Isolation:** Each agent runs in its own environment, preventing resource conflicts.
* **Simplified Management:** Cloud Run handles the underlying infrastructure, allowing developers to focus on the agent logic.
* **Inter-service Communication:** The Orchestrator will invoke the Framework Agents using their secure Cloud Run service URLs, which will be passed to the Orchestrator as `AgentTool` configurations.

---

## 7. Agent-to-Agent (A2A) Communication

### 7.1. Orchestration via ParallelAgent

The primary mechanism for inter-agent communication and concurrent execution is the ADK's **`ParallelAgent`**. The Orchestrator will dynamically configure and run a `ParallelAgent` to manage both the initial and final analysis phases.

**Workflow:**

1. After the user selects the four frameworks, the Orchestrator identifies the corresponding `AgentTool` instances.
2. It instantiates a `ParallelAgent`, providing the four selected agent tools as its `sub_agents`.
3. The Orchestrator then invokes the `run` method on this `ParallelAgent`, passing the required context.
4. The ADK runtime handles the concurrent execution, calling all four Framework Agents in parallel.
5. The `ParallelAgent` completes its execution only after all four sub-agents have returned their JSON responses.
6. The Orchestrator then retrieves the results from the session state to proceed with the next phase of the workflow.

This approach ensures that the analysis is performed as efficiently as possible while maintaining centralized control within the Orchestrator.

### 7.2. Invocation via AgentTool

Each of the 10 Framework Agents is wrapped as an `AgentTool` and made available to the Orchestrator. This abstraction allows the Orchestrator's `ParallelAgent` to invoke the Framework Agents via their secure Cloud Run service URLs without needing to manage the underlying HTTP requests directly.

### 7.3. Passing Context

The `ParallelAgent` and its underlying `AgentTool` instances will automatically handle the passing of the necessary context to each Framework Agent. This includes the user's `original_query` for the first pass and the full `shared_context` for the second pass.

---

## 8. Data Persistence (Firestore & Cloud Storage)

### 8.1. Firestore Database Design

The primary data store for the system will be **Google Firestore**. It will be structured using three distinct top-level collections to ensure a clear separation between static application data, dynamic session data, and user history.

#### 8.1.1. `frameworks` Collection (Static App Data)

This collection holds the static data for the 10 decision-making frameworks. It is populated once by a setup script and is read-only during normal application execution.

* **Purpose:** Stores pre-computed vector embeddings for efficient semantic ranking and provides a single source of truth for framework descriptions.
* **Structure (per document):**

    ```json
    {
      "name": "Cost-Benefit Analysis",
      "description": "A systematic process for calculating and comparing benefits and costs of a decision.",
      "embedding": [0.012, -0.045, ..., 0.089]
    }
    ```

#### 8.1.2. `users` Collection (User History)

This collection links an authenticated user to all of their decision-making sessions, enabling history and restart capabilities.

* **Purpose:** To maintain a denormalized, read-optimized list of all analyses a user has initiated, suitable for displaying a rich history view.

* **Structure (per document, ID is Firebase Auth UID):**

    ```json

    {
      "user_id": "firebase_auth_user_id",
      "sessions": [

        {
          "session_id": "session_abc123",
          "query": "Should we migrate to microservices?",
          "recommendation": "PROCEED with phased migration.",
          "confidence": "85%",
          "cost_usd": 0.75,
          "created_at": "2025-11-07T10:00:00Z",
          "status": "complete"
        },

        {
          "session_id": "session_def456",
          "query": "Which vendor should we choose for our new CRM?",
          "recommendation": null,
          "confidence": null,
          "cost_usd": 0.15,
          "created_at": "2025-11-08T14:30:00Z",
          "status": "in_progress"
        }
      ]
    }

    ```

#### 8.1.3. `sessions` Collection (Dynamic Session State)

This collection stores the detailed, real-time state for each individual decision-making session.

* **Purpose:** To serve as the comprehensive state record for a single, active workflow.
* **Structure (per document):**

    ```json
    {
      "session_id": "unique_session_id",
      "user_id": "firebase_auth_user_id",
      "query": "The user's initial decision query.",
      "ranked_frameworks": [
        {"name": "Pros_and_Cons_Agent", "score": 95, ...}
      ],
      "selected_frameworks": [
        "Pros_and_Cons_Agent", "SWOT_Agent", ...
      ],
      "qa_state": {
        "Pros_and_Cons_Agent": {
          "status": "needs_information",
          "questions": ["...", "...", "..."],
          "answers": ["...", "...", "..."]
        },
        ...
      },
      "agent_reports": {
        "Pros_and_Cons_Agent": {
          "pros": ["..."], "cons": ["..."], "caveat": "..."
        },
        ...
      },
      "final_recommendation": {
        "recommendation": "PROCEED with phased migration.",
        "rationale": "A synthesis of the key findings from all frameworks, highlighting consensus points and strategic advantages.",
        "caveats": [
          "The SWOT analysis identified a potential risk due to limited in-house cloud expertise.",
          "The Pros & Cons analysis noted a short-term increase in operational complexity."
        ],
        "confidence_score": "85%"
      },
      "cost_usd": 0.75,
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
    ```

### 8.2. Cloud Storage for Large Artifacts (Future Use)

While not required for the initial implementation, **Google Cloud Storage** can be integrated later if agents need to generate or process large files (e.g., detailed PDF reports, large datasets for analysis). For the current scope, all data exchange can be handled via JSON payloads and stored within the Firestore document.

---

## 9. Next Steps

### 9.1. Phase 1: Orchestrator and Core Services Setup

1. **Initialize ADK Projects:** Create the directory structure under `/services` for the Orchestrator and all 10 Framework Agents. Initialize each as a Python ADK project.
2. **Implement Orchestrator Tools:** Develop the full business logic for the Orchestrator in `/services/orchestrator/app/tools.py`, including the framework ranking algorithm.
3. **Configure Firestore:** Set up the Google Cloud project with Firestore enabled and configure the necessary security rules.
4. **Pre-compute Framework Embeddings:** Create and run a one-time setup script (`scripts/setup_framework_embeddings.py`). This script will populate the `frameworks` Firestore collection by generating a vector embedding for each of the 10 framework descriptions using the `models/text-embedding-004` API.
5. **Initial Deployment:** Create Dockerfiles for all services and deploy them to Google Cloud Run to establish the baseline infrastructure and service URLs.

### 9.2. Phase 2: Framework Agent Implementation

1. **Implement Agent Instructions:** For each of the 10 Framework Agents, copy the full instruction set from this document into its `agent.py` file.
2. **Implement Sufficiency Analysis Logic:** For each agent, develop the Python logic to perform the two-stage Information Sufficiency Analysis as defined in Section 4. This logic will be part of the agent's main execution flow.
3. **Develop Output Formatting:** Ensure each agent's final output strictly adheres to the required JSON format, including the conditional `information_gaps` field.

### 9.3. Phase 3: Integration and Testing

1. **Configure Agent Tools:** Update the Orchestrator's agent definition with the final Cloud Run URLs for each of the 10 Framework `AgentTool` instances.
2. **End-to-End Testing:** Conduct comprehensive tests of the entire workflow, covering various user queries and decision types.
3. **Error Handling:** Implement robust error handling for scenarios such as agent timeouts, malformed JSON responses, or failures in the Q&A loop.

---

## 10. Backend Implementation Plan

This section provides a developer-focused, step-by-step plan for building the backend system based on the architectural design defined in this document.

### Phase 1: Core Setup & Orchestrator Foundation

* **Task 1.1:** Set up the monorepo structure with directories for `services/orchestrator` and `scripts`.
* **Task 1.2:** Implement the `scripts/setup_framework_embeddings.py` script. Run it to populate the `frameworks` collection in Firestore with the full descriptions and vector embeddings.
* **Task 1.3:** Implement the Orchestrator's `rank_frameworks` tool in `services/orchestrator/app/tools.py`, including the full Multi-Criteria Scoring Algorithm with semantic relevance.
* **Task 1.4:** Create the basic `agent.py` for the Orchestrator, defining it as an `LlmAgent` and including the `rank_frameworks` tool.
* **Task 1.5:** Create the `Dockerfile` for the Orchestrator and deploy a placeholder version to Google Cloud Run to verify the setup and obtain an initial service URL.

### Phase 2: Framework Agent Implementation

* **Task 2.1:** Create the service directories for all 10 Framework Agents (e.g., `services/framework-agent-pros-cons`).
* **Task 2.2:** For a single "template" agent (e.g., `pros_cons`), implement the full `agent.py`. This includes the prompt engineering strategy that loads the knowledge base from its markdown file and wraps it in the operational prompt defining the two-pass logic.
* **Task 2.3:** Copy and adapt this template for the other 9 agents, ensuring each `agent.py` loads its own specific markdown file from the `scripts/framework_descriptions/` directory.
* **Task 2.4:** Create Dockerfiles for all 10 Framework Agents and deploy them to Google Cloud Run to obtain their service URLs.

### Phase 3: Full Workflow Integration & Finalization

* **Task 3.1:** Implement the remaining Orchestrator tools in `tools.py`: `store_user_selection`, `manage_interactive_qa`, `invoke_framework_agents`, and `synthesize_final_recommendation`.
* **Task 3.2:** Update the Orchestrator's `agent.py` to include all its new tools. Configure the `AgentTool` instances for each of the 10 Framework Agents, pointing to their deployed Cloud Run URLs.
* **Task 3.3:** Implement the logic within the `invoke_framework_agents` tool to dynamically create and run the `ParallelAgent` for concurrent analysis.
* **Task 3.4:** Implement the full data persistence logic within the Orchestrator's tools to correctly read from and write to the `users` and `sessions` collections in Firestore, managing the complete lifecycle of a user's analysis.
* **Task 3.5:** Conduct end-to-end integration testing of the entire backend workflow.
