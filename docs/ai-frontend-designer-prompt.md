# Prompt for AI Frontend Designer: FourSight Application (Refined to Replicate `frontend style.jpg`)

## 1. Project Overview

You are tasked with designing the user interface for **FourSight**, a multi-agent decision analysis application. The application helps users make complex decisions by leveraging a suite of 10 specialized AI agents, each an expert in a specific decision-making framework (e.g., SWOT, Cost-Benefit Analysis).

The core user journey is as follows:

1. The user inputs a decision they are facing (e.g., "Should I expand my business into a new market?").
2. An **Orchestrator Agent** ranks the 10 frameworks for relevance.
3. The user selects a "team" of four frameworks.
4. The user participates in an interactive Q&A session with the agents to provide more context.
5. The agents perform their analysis in parallel.
6. The Orchestrator synthesizes the results into a single, actionable recommendation.
7. Users can view their analysis history and key metrics on a dashboard.

## 2. Core Design Philosophy & Aesthetic

- **Theme:** **Claymorphism / Modern Layered Design**. Tactile UI with soft rounded shapes and layered depth via subtle outer and inner shadows. Clean, modern, professional, and focused — avoid cartoonish elements.
- **Design Direction:** **Clarity in Motion**. Smooth micro-interactions, purposeful color, and responsive feedback to guide focus. Uncluttered layout that makes complex information digestible.
- **Primary Technologies:** **Next.js/React + TypeScript**, using **ShadCN UI** components; prototyping with **Firebase Studio**.

### 2.1 Design Tokens (replicate `frontend style.jpg` with decided palette)
- Use the decided color palette and tokens consistently across all screens.
- Base tokens for light theme (aligned with `ux-design-directions.html`):
  - `--background: #F0F0F3`
  - `--card-background: rgba(255, 255, 255, 0.6)`
  - `--border-color: #E5E5E7`
  - `--foreground: #1a1a1a`
  - `--primary: #7C3AED`
  - `--primary-foreground: #FFFFFF`
  - `--secondary: #A1A1AA`
  - `--secondary-foreground: #1a1a1a`
  - `--success: #22C55E`
  - `--destructive: #EF4444`
  - `--radius: 12px`
  - `--shadow-light: 0 8px 24px rgba(0,0,0,0.05)`
  - `--shadow-dark: inset 0 2px 4px rgba(0,0,0,0.05)`
  - Apply a very subtle background SVG pattern at ~4% opacity under content.

### 2.2 Component Specs (visual replication)
- Cards: `border: 1px solid var(--border-color)`, `background: var(--card-background)`, `backdrop-filter: blur(10px)`, `border-radius: var(--radius)`, `box-shadow: var(--shadow-light)`; hover uses slightly higher opacity and shadow.
- Buttons: primary uses `--primary` / `--primary-foreground`, medium radius, semi-bold text; secondary uses neutral greys.
- Badges/Tags: minimal border, subtle shadow; color-coded by framework mapping.
- Spacing scale: `8 / 12 / 16 / 24 / 32` for padding and gaps.
- Typography: Sans `Montserrat` or system font; weights 500–700 for headers; body 400.

### 2.3 Navigation Blueprint (as in `frontend style.jpg`)
- **Top Nav (fixed):** Height ~64px, glassy card background, bottom border using `--border-color`. Left: brand `FourSight` in `--primary`; right: user avatar and name.
- **Floating Secondary Nav (centered under top nav):** Button group: `Dashboard`, `+ New Analysis`, `History`, `Framework Library`. Active state: `--primary` background, white text, subtle shadow.
- Maximize horizontal workspace; avoid left sidebar in desktop. On mobile, collapse into a bottom tab bar.

## 3. Key UI Components & Patterns

### 3.1. Two-Tiered Top Navigation (Story 1.4)

- **Main Top Bar (Fixed):**
  - **Center:** "FourSight" logo and name.
  - **Far Right:** User profile icon and a settings icon.
- **Floating Navigation Bar (Below Main Bar, Centered):**
  - Buttons: "Dashboard", "+ New Analysis", "History", "Framework Library".
  - The active page's button must be highlighted (purple background, white text).

### 3.2. Agent/Framework Cards

- Core component used in Framework Library, Selection, Q&A Cockpit.
- Each of the 10 frameworks (and the Orchestrator) uses a centralized color (Story 4.5); card border reflects that color.
- Card anatomy: Title, short rationale, color border, red `X` pill button for deselect in top-right.
- Card visuals: Claymorphism spec above; maintain consistent transparency to reveal subtle pattern.

### 3.3. Modals

- Used for confirmations (e.g., starting a new analysis while one is in progress, Story 1.7) and error handling (e.g., trying to select a fifth framework, Story 2.3).
- Should have a consistent, clean design that overlays the current view.

### 3.4. Charts & Visualizations
- Framework Frequency (bar chart) and Confidence Over Time (histogram) must use the base palette and framework colors for series, with accessible contrast on axes and labels.

### 3.5. Micro-interactions
- Hover: elevate cards by increasing opacity and shadow; scale by 1.01.
- Active nav button: soft inner shadow to imply pressed state.
- Loading: linear shimmer on cards and subtle pulse on primary CTA.

## 4. Screen-by-Screen Breakdown

### 4.1. Login & Registration (Stories 1.1, 1.2)

- **Goal:** Standard, secure user authentication.
- **Components:**
  - Clean, centered forms for both login and registration.
  - Inputs for email and password (masked).
  - Clear buttons for submission.
  - Links to toggle between the login and registration forms.

### 4.2. Dashboard (Stories 1.3, 1.8)

- **Goal:** Provide the user with an at-a-glance "Productivity Hub" of their activity.
- **Layout:** A clean grid or card-based layout.
- **Components:**
  - **Key Metrics Cards:**
    - Total decisions analyzed.
    - Average confidence level.
    - Total LLM costs ($USD).
  - **Framework Frequency Chart:** A bar chart showing how often each framework has been used.
  - **Confidence Level Over Time Graph (Histogram):**
    - Title: "Confidence Level Over Time".
    - Y-axis: "Low", "Medium", "High". X-axis: Time (daily).
    - Default view: Last 30 days.
    - Inline filter chips above the chart for frameworks (use centralized colors).
    - Hover tooltips on bars showing date and confidence level.
  - **Primary CTA:** "Start New Analysis" centered below metrics, primary style.

### 4.3. New Analysis Page (Story 2.1)

- **Goal:** A focused starting point for the core workflow.
- **Components:**
  - Prominent Header: "What decision are you facing?".
  - Large text input field with placeholder text.
  - Instructional helper text below the input.
  - A 2x2 grid of clickable example query cards to populate the input field.
  - A primary "Submit" button.

### 4.4. Framework Selection Page (Story 2.3)

- **Goal:** Allow the user to review and customize their "AI Strategy Team".
- **Components:**
  - Header: "Assemble Your AI Strategy Team".
  - **2x2 Grid (Top):** Displays the top 4 recommended frameworks.
    - Each card shows: Title, one-sentence rationale, a colored border matching the framework's color, and a red "X" to deselect.
  - **Non-Selected List (Bottom):** The other 6 frameworks displayed as styled, clickable buttons with colored borders.
    - Hovering over a button shows a tooltip with its rationale.
  - **"Start Analysis" Button:** Enabled only when exactly four frameworks are in the 2x2 grid.
  - Maintain consistent transparency to reveal background pattern; use card hover spec.

### 4.5. Q&A Cockpit (Story 2.4)

- **Goal:** Facilitate an organized, parallel Q&A session with the four selected agents.
- **Layout:** A two-pane view.
- **Left Pane (Orchestrator Chat):**
  - Displays a high-level summary of agent statuses (e.g., "SWOT Agent: Ready", "Cost-Benefit Agent: Needs more information").
- **Right Pane (Agent Chat Grid):**
  - A 2x2 grid of color-coded chat cards, one for each agent.
  - Agents that are "Ready" display a status message.
  - Agents needing info display their first question.
  - Users can type answers in any agent's chat window. Upon submission, the next question appears, until all questions for that agent are answered.
  - Chat bubble colors: agent title bar uses framework color; content area remains neutral.

### 4.6. Final Recommendation Page (Stories 2.5, 2.6, 2.7, 2.8)

- **Goal:** Present the final, synthesized output and allow for detailed drill-down.
- **Layout:** The same two-pane "Cockpit" view from the Q&A session.
- **Left Pane (Orchestrator Chat):**
  - Displays the final, synthesized recommendation from the Orchestrator.
  - **Structure:**
    1. Recommendation & Confidence Score.
    2. Executive Summary.
    3. Key Supporting Points.
    4. Key Risks and Contradictions (including consolidated `caveats`).
  - Displays total analysis cost (USD and tokens).
  - Buttons: "Acknowledge" and "Restart with Other Frameworks".
- **Right Pane (Agent Report Grid):**
  - The 2x2 grid now shows the full, final, un-synthesized report from each individual agent.
  - If an agent had missing info, its report must clearly display an "Information Gaps" section.
  - The synthesized recommendation headline uses `--primary` color.

### 4.7. History Page (Story 3.1)

- **Goal:** Allow users to review all past analyses.
- **Layout:** A scrollable, two-column grid of history cards.
- **Components (per card):**
  - Original decision query.
  - Final recommendation.
  - Confidence level (styled tag).
  - Date and Cost.
  - The four frameworks used (styled tags).
  - A "Retry with Other Frameworks" button.

### 4.8. Framework Library Page (Story 1.6)

- **Goal:** An informational page for users to learn about the available frameworks.
- **Layout:** Two vertical sections.
- **Left Section (Wide):** Displays the full details (title, description) of the selected framework.
- **Right Section (Thin):** A vertical navigation list of all 10 frameworks as color-coded cards (title only). The selected framework is highlighted (bold border and slight elevation).

### 4.9. Settings Page (Story 1.5)

- **Goal:** A placeholder for future account management.
- **Layout:** A simple page with the title "Settings". Can be a basic placeholder for now.

## 5. Non-Functional Requirements

- **Responsiveness:** The entire application must be fully responsive and usable on a range of screen sizes, from mobile to desktop.
- **Performance:** The UI must remain fluid and responsive, especially during backend processing. Use loading indicators to provide feedback to the user (Story 4.1).
 - **Accessibility:** Verify color contrast (WCAG AA). Ensure keyboard navigation for cards and nav.
 - **Consistency:** Centralize framework colors; no ad-hoc color choices in components.

## 6. Centralized Color Mapping (Story 4.5)

- Maintain framework color mapping in Firestore (`frameworks.color`). For prototyping, default mapping:
  - `swot_agent: #3B82F6` (blue)
  - `pros_cons_agent: #06B6D4` (cyan)
  - `cost_benefit_agent: #10B981` (green)
  - `weighted_matrix_agent: #8B5CF6` (purple)
  - `five_whys_agent: #F59E0B` (amber)
  - `five_ws_and_h_agent: #6366F1` (indigo)
  - `ten_ten_ten_agent: #14B8A6` (teal)
  - `decide_model_agent: #84CC16` (lime)
  - `kepner_tregoe_agent: #EC4899` (pink)
  - `rational_decision_making_agent: #F43F5E` (rose)
  - `orchestrator_agent: #7C3AED` (accent purple)
- Components must reference these colors via a centralized utility (no hard-coded inline colors).

## 7. Animation & Motion Guidelines
- Duration: 150–200ms for hover/press, 300–400ms for modal open/close.
- Easing: Standard `cubic-bezier(0.2, 0, 0, 1)`.
- Avoid large parallax; keep motion subtle and informative.

## 8. Prototyping in Firebase Studio
- Import this prompt and `frontend style.jpg` as the visual reference.
- Configure Style Tokens based on Section 2.1 before component generation.
- Use ShadCN primitives where possible; apply tokens and variants:
  - Button variants: `primary`, `secondary`, `destructive`.
  - Card component with `title`, `subtitle`, `borderColor` prop.
  - Badge component with `color` prop from framework mapping.
- Generate screens following Section 4; verify visual parity with `frontend style.jpg`.

## 9. Deliverables
- High-fidelity mockups for each screen, matching `docs/frontend style.jpg` with the decided palette.
- A component library (tokens, cards, buttons, badges, charts) aligned with Claymorphism.
- Motion specs and accessibility notes.
- Exported CSS variables/theme file for implementation.

## 10. Visual Parity Checklist (against `frontend style.jpg`)
- Top nav uses glassy card background and `--primary` brand accent.
- Floating secondary nav centered, with clear active/hover states.
- Framework selection 2x2 grid with colored borders and red `X` pills.
- Subtle background pattern visible through semi-transparent cards.
- Consistent spacing and typography scale across screens.
