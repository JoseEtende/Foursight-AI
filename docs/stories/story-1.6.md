# Story 1.6: Framework Library

**ID:** S1.6
**Epic:** E01 - User Authentication & Dashboard
**User Story:** As a user, I want to see a list of all available frameworks and be able to select one to view its detailed description.

---

## Acceptance Criteria

1. The "Framework Library" page must be divided into two vertical sections: a wide "details view" on the left and a thinner "navigation list" on the right.
2. The right section must display all 10 frameworks as a vertical list of color-coded cards, showing only their titles.
3. The left section must display the full details of the currently selected framework, including its title and description.
4. Upon loading the page, the first framework in the navigation list is selected by default, and its details are shown in the details view.
5. The selected framework in the right-hand list must have a clear visual indicator (e.g., a highlighted border or background color).
6. Clicking on a different framework card in the right-hand navigation list must update the left-hand details view to show the information for the newly selected framework.
7. This page is for informational purposes and does not initiate an analysis.

---

## Backend Implementation

- The framework titles and descriptions will be fetched from the `frameworks` collection in Firestore, as detailed in story S5.1.
- The backend will need to provide an endpoint to retrieve all framework data.
