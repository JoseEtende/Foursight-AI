# Story 4.5: Centralized Color Assignment

**ID:** S4.5
**Epic:** E04 - System-Wide Non-Functional Requirements
**User Story:** As a developer, I want a centralized function to programmatically assign a unique and consistent color to each of the 10 frameworks and the orchestrator, so that all UI elements are visually consistent and distinguishable.

---

## Acceptance Criteria

1. A utility function or service must be created for color assignment.
2. The function must maintain a predefined mapping of the 10 frameworks and the orchestrator to specific, visually distinct hex color codes.
3. Any UI component that needs to display a color for a framework (e.g., buttons, cards, chart elements) must use this central function.
4. The colors chosen should be accessible and provide good contrast.
5. The color mapping must be easily updatable in one location.

---

## Backend Implementation

* The color mapping will be stored in the `frameworks` collection in Firestore, with each framework document having a `color` field, as detailed in story S5.1.
* The frontend will fetch this color information along with the other framework data.
