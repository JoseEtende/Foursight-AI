# Epic Technical Specification: User Authentication & Dashboard

Date: 2025-11-08
Author: Jose
Epic ID: E01
Status: Draft

---

## Overview

This epic covers the foundational user-facing features of the FourSight application. It includes the entire user lifecycle from registration and login to viewing their personalized dashboard. The primary goal is to provide a secure and engaging entry point to the application's core decision-analysis functionalities. This epic will implement the main navigation structure and the dashboard that provides users with at-a-glance metrics about their usage and performance on the platform.

## Objectives and Scope

**In Scope:**

* User registration with email and password.
* User login and session management.
* A dashboard displaying total decisions, average confidence level, most used frameworks, and total LLM costs.
* A two-tiered global navigation system.
* A settings page for basic user account management.
* A framework library page to browse available frameworks.
* A safeguard to prevent users from starting a new analysis while one is already in progress.

**Out of Scope:**

* Third-party authentication (e.g., Google, GitHub).
* Advanced user profile settings.
* Role-based access control (RBAC).
* Any part of the core decision analysis workflow itself.

## System Architecture Alignment

This epic aligns with the established serverless architecture. The frontend components will be built using Next.js/React and will interact with Firebase Authentication for user management. The dashboard data will be retrieved from a dedicated `users` collection in Firestore, which will be updated by the backend services upon completion of each analysis. All services will be deployed on Google Cloud Run, ensuring scalability and separation of concerns.

## Detailed Design

### Services and Modules

| Service/Module | Responsibilities | Inputs/Outputs | Owner |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | Render login, registration, and dashboard pages. Manage UI state. | **Inputs:** User credentials, dashboard data from Firestore. **Outputs:** Authentication requests to Firebase, navigation events. | Frontend Team |
| **Firebase Auth** | Handle user creation, authentication, and session persistence. | **Inputs:** User email/password. **Outputs:** JWTs, user session state. | GCP |
| **Firestore Service** | Provide secure access to the `users` and `sessions` collections. | **Inputs:** Authenticated user ID. **Outputs:** User-specific analysis history and metrics. | Backend Team |
| **Orchestrator** | (Future) Update the `users` collection with new analysis data upon completion. | **Inputs:** Completed analysis data. **Outputs:** Writes to Firestore. | Backend Team |

### Data Models and Contracts

**`users` Collection (Firestore):**

```json
{
  "user_id": "string",
  "sessions": [
    {
      "session_id": "string",
      "query": "string",
      "recommendation": "string",
      "confidence": "string",
      "cost_usd": "number",
      "created_at": "timestamp",
      "status": "string"
    }
  ]
}
```

### APIs and Interfaces

* **Firebase Auth SDK:** The frontend will use the standard Firebase client-side SDK for all authentication operations (`createUserWithEmailAndPassword`, `signInWithEmailAndPassword`, `onAuthStateChanged`).
* **Firestore SDK:** The frontend will use the Firestore client-side SDK to read data for the dashboard. Rules will be configured to ensure users can only read their own data.

### Workflows and Sequencing

1. **User Registration:**
    * User fills out the registration form in the Next.js UI.
    * Frontend calls `createUserWithEmailAndPassword`.
    * On success, a new document is created in the `users` collection with the `user_id`.
    * User is redirected to the dashboard.
2. **User Login:**
    * User enters credentials in the login form.
    * Frontend calls `signInWithEmailAndPassword`.
    * On success, the user's session is established, and they are redirected to the dashboard.
3. **Dashboard Loading:**
    * The dashboard component mounts and checks the user's auth state.
    * It queries the `users` collection for the document matching the current `user_id`.
    * It aggregates the data from the `sessions` array to calculate and display the required metrics.

## Non-Functional Requirements

### Performance

* **FR-2.1.2:** Dashboard metrics should load in under 2 seconds. Firestore queries will be optimized with appropriate indexes.
* Authentication actions (login/signup) should complete within 1.5 seconds.

### Security

* **FR-2.1.1:** All authentication will be handled by Firebase Authentication, leveraging its built-in security features.
* Firestore security rules will be implemented to ensure users can only access their own data in the `users` collection.

### Reliability/Availability

* The system relies on the high availability of Firebase Authentication and Firestore, which are managed Google services with strong SLAs.

### Observability

* Frontend errors will be logged.
* Firebase and Firestore usage metrics will be monitored in the Google Cloud Console.

## Dependencies and Integrations

* **Next.js/React:** Frontend framework.
* **Firebase SDK:** For authentication and database interaction.
* **Google Cloud Run:** Deployment target for the frontend application.

## Acceptance Criteria (Authoritative)

1. A new user can create an account using an email and password.
2. An existing user can log in with their email and password.
3. After logging in, the user is redirected to the dashboard.
4. The dashboard correctly displays the total number of decisions analyzed.
5. The dashboard correctly displays the user's average confidence level.
6. The dashboard correctly displays a visualization of the most used frameworks.
7. The dashboard correctly displays the total LLM costs incurred by the user.
8. A two-tiered global navigation bar is present on all main pages.
9. A user can navigate to a placeholder Settings page.
10. A user can navigate to a placeholder Framework Library page.
11. The system prevents a user from starting a new analysis if one is already in progress.

## Traceability Mapping

| AC # | Spec Section(s) | Component(s)/API(s) | Test Idea |
| :--- | :--- | :--- | :--- |
| 1, 2 | Detailed Design | Firebase Auth SDK, UI | E2E test for signup/login flow. |
| 3-7 | Detailed Design | Firestore SDK, UI | E2E test to verify dashboard metrics with mock data. |
| 8-10 | Overview | UI Components | Cypress component tests for navigation bars. |
| 11 | Objectives | UI State Management | Unit test for UI logic that disables the "New Analysis" button. |

## Risks, Assumptions, Open Questions

* **Risk:** Firestore query performance for dashboard aggregations may degrade as the number of sessions per user grows. **Mitigation:** Keep the denormalized data in the `users` collection lean and consider using a Cloud Function to pre-aggregate metrics if needed.
* **Assumption:** The Firebase Authentication free tier will be sufficient for the hackathon's user load.
* **Question:** What specific visualization should be used for the "most used frameworks" on the dashboard? (Decision: A simple bar chart for the MVP).

## Test Strategy Summary

* **Unit Tests:** For any complex UI logic or data transformation functions.
* **Component Tests (Cypress):** For individual UI components like the navigation bars and dashboard widgets.
* **End-to-End (E2E) Tests (Cypress):** To cover the full user registration, login, and dashboard viewing flows. Mock data will be used in Firestore to validate the dashboard metrics.
