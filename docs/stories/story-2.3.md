# Story 2.3: Framework Selection UI

**ID:** S2.3
**Epic:** E02 - Core Decision Analysis
**User Story:** As a user, after submitting my query, I want to see a clear and interactive page where I can review and customize the AI-recommended team of frameworks.

---

## Description

This story defines the user interface for the "Framework Selection" step. After the Orchestrator agent ranks the frameworks, this page displays the top four recommendations in a 2x2 grid. The user can accept this recommendation or easily swap frameworks with others from a provided list before proceeding with the analysis.

---

## Acceptance Criteria

1. The page must have a clear title (e.g., "Assemble Your AI Strategy Team") and a subtitle guiding the user.
2. The interface must feature a 2x2 grid displaying the top 4 recommended frameworks as selectable cards.
3. Each of the 10 frameworks must have a **one-sentence rationale** explaining its suitability for the user's query.
4. **Selected Frameworks (in the 2x2 grid):**
    * Must display the framework's title, rationale, a colored border **matching the framework's assigned color**, and a red "X" icon.
5. **Non-Selected Frameworks (below the grid):**
    * Must be displayed as styled, clickable buttons with a colored border **matching the framework's assigned color**.
    * On hover, a floating card (tooltip) must appear. This card will display the same detailed rationale that is shown for selected frameworks, explaining its suitability for the user's query.
6. **Deselection Interaction:**
    * Clicking the red "X" on a selected card must move that framework to the end of the non-selected list below, leaving an empty slot in the grid.
7. **Selection Interaction:**
    * If there is an empty slot in the grid, clicking a non-selected framework button must move it into the empty slot, turning it into a full card.
8. **Error Handling (Grid Full):**
    * If all four slots in the grid are full, clicking a non-selected framework button must trigger a pop-up modal.
    * The modal must inform the user that four frameworks are already selected and that they must deselect one before adding another.
9. **Primary Action:**
    * A "Start Analysis" button must be present at the bottom of the page.
    * The button is **enabled by default** as the page loads with four frameworks. It must be **disabled** at any time the number of selected frameworks is not exactly four.

---

## Backend Implementation

* The user's final selection of four frameworks will be stored in the `selected_frameworks` field of the session document in Firestore, as detailed in story S5.3.
* Clicking the "Start Analysis" button will trigger the Orchestrator to invoke the selected Framework Agents in parallel, as detailed in story S5.2 and S5.3.
