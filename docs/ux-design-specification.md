# UX Design Specification: FourSight

**Version:** 2.0
**Date:** 2025-11-05
**Author:** BMad UX Designer

---

## 1. Design Philosophy & Direction

### 1.1. Core Principles

The user experience of FourSight will be guided by three core principles:

1. **Clarity in Motion:** The interface must be clean, intuitive, and provide clear visual feedback. Animations and transitions should be purposeful, guiding the user through the complex process of decision analysis without being distracting. The goal is to make a sophisticated backend feel simple and responsive.
2. **Guided Autonomy:** The user is an expert in their domain; the application is the expert in decision analysis. The UI should guide the user by offering intelligent suggestions (like framework selection) but always provide them with the final say and the ability to customize their experience.
3. **Trust Through Transparency:** To build user confidence in the AI-driven recommendations, the system must be transparent. The UI will clearly explain *why* it makes certain suggestions (e.g., framework rationales) and will always allow the user to "look under the hood" at the detailed analysis of individual agents.

### 1.2. Visual Style: "Claymorphism & Translucence"

The visual aesthetic is directly inspired by the provided `claymorphism_dashboard.png` screenshot. It's a "Modern Layered Design" characterized by:

- **Claymorphism:** Soft, rounded, layered cards with subtle inner and outer shadows to create a sense of depth and tactile interaction, as seen in the reference image.
- **Translucent Cards:** Card backgrounds will feature a subtle "frosted glass" transparency. This enhances the layered effect, allowing the background to be partially visible, creating a modern and airy feel.
- **Typography:** The application will use the "Montserrat" font family from Google Fonts. **Bold** weight will be used for titles, headings, and key information to establish a strong visual hierarchy, while regular weight will be used for body text.
- **Vibrant Accent Colors:** A palette of distinct, vibrant colors will be programmatically assigned to each of the 10 frameworks and the orchestrator. This ensures visual consistency and helps the user immediately identify different agents and components across the application.
- **Minimalism:** The UI will be uncluttered, focusing the user's attention on the task at hand. White space is a key component of the design.

### 1.3. Navigation

As defined in the user stories (S1.4), the application will **not** use a traditional sidebar. Instead, it will feature a modern, two-tiered header with a floating navigation bar for main page access. This approach maximizes the user's horizontal workspace.

---

## 2. Wireframes & Component Breakdown

This section details the UI components required to fulfill the user stories.

### Epic 1: User Authentication & Dashboard

#### **S1.1 & S1.2: User Registration & Login**

- **Component:** Auth Form
- **Description:** A single, clean form centered on the page. It will have a toggle to switch between "Login" and "Register" states.
- **Elements:**
  - Email Input Field
  - Password Input Field (masked)
  - "Login" / "Register" Button
  - Toggle link to switch modes.

#### **S1.4: Two-Tiered Top Navigation**

- **Component:** Main Top Bar
- **Description:** A fixed bar at the very top of the screen.
- **Elements:**
  - **Center:** "FourSight" Logo.
  - **Right:** User Profile Icon, Settings Icon.
- **Component:** Floating Navigation Bar
- **Description:** A centered, floating bar situated just below the Main Top Bar.
- **Elements:**
  - Buttons: "Dashboard", "+ New Analysis", "History", "Framework Library".
  - **Active State:** The button for the current page will have a distinct style (purple background, white text).

#### **S1.3 & S1.8: User Dashboard**

- **Layout:** A two-column layout.
- **Left Column (Wider):**
  - **Component:** "Productivity Hub" Card
    - **Elements:**
      - Metric: "Total Decisions Analyzed"
      - Metric: "Average Confidence Level"
      - Metric: "Total LLM Costs"
  - **Component:** "Confidence Level Over Time" Histogram (S1.8)
    - **Elements:**
      - Chart Title
      - Y-Axis (Low, Medium, High)
      - X-Axis (Time/Date)
      - Interactive Bars with Tooltips
- **Right Column (Narrower):**
  - **Component:** "Framework Usage" Chart
    - **Description:** A vertical bar chart showing the frequency of each framework's use.
  - **Component:** Framework Filter List (for S1.8)
    - **Description:** A vertical list of framework names to filter the histogram.

### Epic 2: Core Decision Analysis

#### **S2.1: Decision Analysis Page (Query Input)**

- **Layout:** Single column, centered content.
- **Elements:**
  - Main Header: "What decision are you facing?"
  - Large Text Area for user query with placeholder text.
  - Helper text below the input.
  - **Component:** 2x2 Grid of "Example Query" Cards.
  - "Submit" Button.

#### **S2.3: Framework Selection UI**

- **Layout:** Single column.
- **Elements:**
  - Main Header: "Assemble Your AI Strategy Team"
      -   **Component:** 2x2 Grid for the 4 selected frameworks.
          -   **Card State (Selected):** Displays framework title, rationale, a colored border that **matches the framework's assigned color**, and a red "X" icon.
      -   **Component:** List of non-selected frameworks.
          -   **Element State (Button):** Clickable button with the framework title and a colored border that **matches the framework's assigned color**.
            -   **Hover State:** Hovering over a button reveals a floating card (tooltip). This card will display the same detailed rationale that is shown for selected frameworks, explaining its suitability for the user's query.
  - "Start Analysis" Button. This button is **enabled** if and only if there are exactly four frameworks selected. It is enabled by default, as the page loads in this state. It becomes **disabled** if the user deselects one or more frameworks, and re-enables once the count is exactly four again.

#### **S2.4: Orchestrated Q&A Session**

- **Layout:** Two-pane "Q&A Cockpit".
-   **Left Pane (Orchestrator):**
    -   **Component:** Main Chat Window
        -   **Content:** After the initial analysis, this window displays a message: "All agents have completed their initial analysis." This is followed by a color-coded, bulleted list showing the status of each of the four agents (e.g., "SWOT Agent: Ready to proceed", "Cost-Benefit Agent: Needs more information").
-   **Right Pane (Agents):**
    -   **Component:** 2x2 Grid of Agent Chat "Cards".
        -   **Card Content:** Each card is a mini-chat window for a specific, color-coded agent.
        -   **"Ready" State:** Agents that do not need more information will display a status message (e.g., "Ready to proceed").
        -   **"Needs Info" State:** Agents that need more information will immediately display their first question.
        -   **Q&A Interaction:** When the user answers a question, the agent will sequentially ask its next question, up to a maximum of three. Once the final question for an agent is answered, its card will update to display the "Ready to proceed" status.
        -   **Asynchronous Answering:** The user can answer questions from any agent in any order; they are not locked into completing one agent's Q&A before addressing another.
        -   **Input:** A single text input at the bottom of the pane, which directs the user's response to the correct agent Q&A flow.

#### **S2.6 & S2.7: Synthesized Recommendation & Drill-Down**

- **Layout:** A main content area with selectable views.
- **Component:** Tab Navigation
  - **Tabs:** "Synthesized Recommendation", [Agent 1 Name], [Agent 2 Name], [Agent 3 Name], [Agent 4 Name].
-   **"Synthesized Recommendation" View (Default):**
    -   Prominently displayed Recommendation & Confidence Score.
    -   Section: Executive Summary.
    -   Section: Key Supporting Points.
    -   Section: Key Risks and Contradictions.
    -   **Section: Actions & Metadata:**
        -   Button: "Acknowledge"
        -   Button: "Restart with Other Frameworks"
        -   Display: Total Cost (e.g., "$0.04")
        -   Display: Total Tokens (e.g., "15,234 tokens")
- **Agent Drill-Down Views:**
  - Each agent tab, when clicked, reveals the full, un-synthesized report from that agent.
  - **S2.8:** If applicable, this view will contain the "Information Gaps" section.

### Epic 3: Analysis History & Retry

#### **S3.1 & S3.2: Analysis History Page**

- **Layout:** A two-column, scrollable grid.
- **Component:** History Card
  - **Description:** A "Modern Layered Design" card for each past analysis.
  - **Elements:**
    - Decision Query
    - Final Recommendation
    - Confidence Level (as a styled tag)
    - Date
    - Cost
    - Frameworks Used (as styled tags)
    - "Retry with Other Frameworks" Button.

### Epic 4: Global & Modal Components

#### **S1.7: "Ongoing Analysis" Modal**
-   **Component:** Confirmation Modal
-   **Trigger:** User clicks "+ New Analysis" while an analysis is running.
-   **Elements:**
    -   **Title:** "Analysis in Progress"
    -   **Body:** "Starting a new analysis will terminate the current one."
    -   **Buttons:** "Cancel", "Terminate & Start New"

#### **S2.3: "Framework Grid Full" Modal**
-   **Component:** Information Modal
-   **Trigger:** User attempts to select a fifth framework.
-   **Elements:**
    -   **Title:** "Strategy Team Full"
    -   **Body:** "You must deselect a framework before adding a new one."
    -   **Button:** "OK"

#### **S2.5 & S4.1: "Analysis in Progress" Indicator**
-   **Component:** Loading Indicator Overlay
-   **Trigger:** Displayed after the Q&A session is complete and parallel analysis begins.
-   **Description:** A full-screen overlay with a "frosted glass" blur effect on the background content. Centered in the overlay will be a dynamic, color-shifting animation that smoothly cycles through the four colors of the active agent team, reinforcing the "Clarity in Motion" principle.

---

## 3. Centralized Color Scheme (S4.5)

A centralized utility will map each of the 10 frameworks and the orchestrator to a unique, vibrant, and accessible color. This color will be used consistently across all UI components to represent that agent/framework, including:

- Card borders in the Framework Selection UI.
- Agent chat windows in the Q&A Cockpit.
- Data visualizations on the Dashboard (e.g., bar charts).
- Styled tags in the History cards.

This ensures immediate visual recognition for the user, reinforcing the "team of agents" concept.
