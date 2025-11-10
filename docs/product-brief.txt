# Product Brief: FourSight

**Date:** 2025-11-03
**Author:** Jose
**Context:** Google Cloud Run Hackathon (run.devpost.com)

---

## Executive Summary

FourSight is an innovative, multi-agent decision analysis system designed for the Google Cloud Run Hackathon. It addresses the common problem that professionals often make decisions with a limited analytical scope. FourSight solves this by intelligently selecting four relevant decision-making frameworks from a library of ten, executing them in parallel with Gemini 2.5 Pro, and synthesizing the results into a single, actionable recommendation. This serverless application, built with the Python ADK and Next.js, showcases a seamless, collaborative workflow where a team of AI agents assists a user in making confident, well-informed decisions.

---

## Core Vision

### Problem Statement

Professionals make critical decisions daily but often lack the diverse insights needed to do so with high confidence. The core problem is the limited analytical scope they employ, which can lead to bias and suboptimal outcomes. FourSight directly addresses this by implementing multiple, contextually-relevant decision-making frameworks in parallel to ensure a comprehensive, multi-faceted analysis.

### Proposed Solution

FourSight provides a user with a team of AI agents that act as expert consultants. A user enters a decision they need to make, and an orchestrator agent analyzes the query, ranks 10 available frameworks, and suggests the four most relevant ones. The user can validate or customize this selection. The system then facilitates an optional, brief, iterative Q&A session to gather sufficient context before the four agents run their analyses in parallel. Finally, the orchestrator synthesizes their findings into a single, clear recommendation, while still allowing the user to review the detailed output from each individual agent.

### Key Differentiators

-   **Parallel Framework Execution:** The most innovative aspect is moving beyond a single-framework analysis. By running four distinct frameworks simultaneously, FourSight provides a richer, more robust foundation for decision-making.
-   **Intelligent Orchestration:** The system doesn't just run frameworks; it intelligently ranks and recommends the most suitable ones based on the user's specific query, acting as an expert consultant.
-   **Collaborative AI Team:** The "wow" moment of the user experience is witnessing a team of four specialized AI agents seamlessly collaborating to assist in solving the user's problem.

---

## Target Users

### Primary Users

The ideal user is a **business strategist** who regularly needs to make complex decisions to foster business growth. However, the system is designed to be intuitive enough for any professional or individual facing a significant decision in a business, professional, or personal setting.

### User Journey

1.  The strategist logs in and is presented with a clean interface to enter their decision query (e.g., "Should we enter the European market?").
2.  The Orchestrator Agent analyzes the query and presents the top 4 recommended frameworks (e.g., SWOT, Cost-Benefit, 5Ws & H, Weighted Decision Matrix) with a brief rationale for each. The other 6 frameworks are visible below.
3.  The strategist can hover over any non-suggested framework to see its rationale, deselect a suggested one, and add an alternative.
4.  Once the strategist validates the four frameworks, the system may initiate a brief, targeted Q&A session if any agent requires more context.
5.  After the context is sufficient, the analysis runs automatically.
6.  The strategist receives a clear, highlighted recommendation from the Orchestrator.
7.  They can read the supporting rationale and also dive into the detailed analysis from each of the four framework agents.
8.  The outcome is a confident, data-backed decision to drive their business forward.

---

## Success Metrics

The success of FourSight will be measured against three key metrics, reflecting the core value proposition and hackathon judging criteria:

1.  **Confidence (Primary):** The primary goal is to increase the user's confidence in their decision. This can be qualitatively measured by the clarity and thoroughness of the final recommendation.
2.  **Time to Decision:** The system should significantly reduce the time it takes for a user to move from problem statement to a well-reasoned decision.
3.  **Cost Efficiency:** As a serverless application, success is also measured by the efficiency of LLM token usage, translating directly to operational cost.

---

## MVP Scope

### Core Features

The following features are "must-haves" for a successful hackathon demo:

1.  **User Query Input:** A simple, clear interface for the user to enter their decision.
2.  **Framework Recommendation & Validation:** The Orchestrator must analyze the query, suggest four frameworks, and allow the user to validate or customize the selection.
3.  **Parallel Agent Execution:** All four selected agent frameworks must run in parallel to perform their analysis.
4.  **Synthesized Recommendation:** The Orchestrator must present a final, consolidated recommendation based on the agents' outputs.
5.  **Individual Agent Drill-Down:** The user must be able to view the individual conclusion and reasoning from each of the four framework agents.
6.  **User Accounts & Persistent History:** Users must be able to create accounts and view their past decision analyses.
7.  **Full Framework Library:** The complete library of 10 decision-making frameworks will be available for selection.

### Out of Scope for MVP

-   Advanced features like file uploads for context.
-   Integration with external data sources or tools.

---

## Risks and Assumptions

-   **Biggest Technical Risk:** The primary technical risk is the complexity of the multi-agent system design, specifically the inter-agent communication (A2A) and API interactions required for the orchestrator to manage the workflow.
-   **Mitigation Plan:** This risk will be mitigated by strictly adhering to the **Python Agent Development Kit (ADK)** provided by Google. We will enforce rigid data schemas using **Pydantic** for all communications and implement **robust, centralized logging** from the outset to quickly diagnose any issues in the communication flow.

---

## Timeline

This project will be executed within the 7-day timeline of the Cloud Run Hackathon, following the detailed implementation plan in the `brainstorming` folder.

---

_This Product Brief captures the vision and requirements for FourSight for the Cloud Run Hackathon._
