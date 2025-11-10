# FourSight Frontend Implementation Guide (Beginner-Friendly)

Version: 2025-11-09

This guide walks you step by step to build the FourSight frontend using Firebase/Firebase Studio, integrate with Firestore and Authentication, and connect to the backend agents on Cloud Run. It is written for beginners and aligns with the system architecture and data contracts described in the repository docs.

## Overview

- Frontend: Next.js/React (deployed to Cloud Run or Firebase App Hosting)
- Auth: Firebase Authentication (Email/Password for MVP)
- Database: Cloud Firestore (collections: `frameworks`, `users`, `sessions`)
- Backend: Orchestrator + 10 Framework Agents on Cloud Run, exposed via ADK `web` server (`/run` endpoint)

References:
- System architecture and data model: `docs/ARCHITECTURE.md`
- Authentication and dashboard: `docs/tech-spec-epic-E01.md`
- Agent workflow and Firestore data fields: `docs/technical-spec.md`
- Frontend UX directions: `docs/ai-frontend-designer-prompt.md`, `docs/ux-design-specification.md`
 - Visual style reference: `docs/frontend style.jpg`

## Design Tokens & Studio Prompt (Replicate the Style Image)

- Use `docs/ai-frontend-designer-prompt.md` in Firebase Studio to guide prototyping and replicate `docs/frontend style.jpg`.
- Base theme tokens (light):
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

- Framework color mapping (centralized, also stored in Firestore as `frameworks.color`):
  - `swot_agent: #3B82F6`
  - `pros_cons_agent: #06B6D4`
  - `cost_benefit_agent: #10B981`
  - `weighted_matrix_agent: #8B5CF6`
  - `five_whys_agent: #F59E0B`
  - `five_ws_and_h_agent: #6366F1`
  - `ten_ten_ten_agent: #14B8A6`
  - `decide_model_agent: #84CC16`
  - `kepner_tregoe_agent: #EC4899`
  - `rational_decision_making_agent: #F43F5E`
  - `orchestrator_agent: #7C3AED`

- Component parity guidelines (match `frontend style.jpg`):
  - Top nav: glassy card background, bottom border using `--border-color`, brand accent uses `--primary`.
  - Floating secondary nav: centered button group with clear active/hover states.
  - Framework selection: 2x2 grid with colored borders and red `X` deselect pills.
  - Subtle background pattern visible under semi-transparent cards; consistent spacing/typography.

- Firebase Studio steps:
  - Import repo and open Design tab.
  - Upload `docs/frontend style.jpg` as the visual reference.
  - Configure the tokens above in the Theme settings.
  - Generate components (cards, buttons, badges) and pages using the prompt; verify parity with the style image.

## Prerequisites

- A Firebase project (can be the same GCP project used for Cloud Run)
- Admin access to Firebase Console
- Node.js 18+ and npm 9+
- GitHub repo access (this repository)
- Cloud Run services deployed (Orchestrator and framework agents), or local dev endpoints

Optional but recommended:
- Firebase Studio to develop and publish the frontend with integrated tooling [Firebase Studio docs](https://firebase.google.com/docs/studio)

## Step 1 — Import the repo into Firebase Studio (or set up locally)

You have two paths. Choose one and stick to it for the MVP:

- Path A: Use Firebase Studio (agentic web IDE)
  - Import the GitHub repo into Firebase Studio.
  - Configure Firebase Authentication and Firestore directly in Studio.
  - Use Studio’s integrated preview and App Hosting to iterate quickly and publish.

- Path B: Local Next.js setup
  - Create a new Next.js app in a `frontend/` folder: `npx create-next-app@latest frontend`
  - Install Firebase SDK: `npm i firebase`
  - Use `.env.local` for Firebase config and backend URLs.
  - Deploy to Cloud Run or Firebase Hosting when ready.

For beginners, Path A (Firebase Studio) is simpler to get started and includes built-in deployment. For long-term alignment with the repo’s architecture, Cloud Run is fine too.

## Step 2 — Configure Firebase Authentication

- In Firebase Console, enable Email/Password sign-in.
- Create a web app under the project to get your client config (`apiKey`, `authDomain`, etc.).
- Add these to your frontend `.env.local`:

```
NEXT_PUBLIC_FIREBASE_API_KEY=... 
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=... 
NEXT_PUBLIC_FIREBASE_PROJECT_ID=... 
NEXT_PUBLIC_FIREBASE_APP_ID=... 
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=...
```

- In Next.js, initialize Firebase:

```ts
// src/lib/firebase.ts
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

Pages to create:
- `/signup` and `/login` using Firebase Auth (`createUserWithEmailAndPassword`, `signInWithEmailAndPassword`).
- Auth guard (redirect unauthenticated users to `/login`).

## Step 3 — Set up Firestore and Security Rules

- Enable Cloud Firestore (production mode).
- Collections:
  - `frameworks`: pre-seeded static data (name, description, embedding)
  - `users`: per-user history and metrics
  - `sessions`: per-analysis session state

Security Rules (from `firestore.rules` in repo):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /frameworks/{frameworkId} {
      allow read: if true;
      allow write: if false;
    }
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.user_id;
    }
    match /sessions/{sessionId} {
      allow create: if request.auth != null && request.auth.uid == request.resource.data.user_id;
    }
  }
}
```

Important consistency note:
- The orchestrator currently writes session data under `artifacts/{APP_ID}/public/data/sessions/{session_id}` (see `services/orchestrator/app/tools.py`). For MVP simplicity, you can:
  - Option 1: Align code to write to top-level `sessions/{session_id}` as the rules expect.
  - Option 2: Extend rules to allow authenticated read/write for `artifacts/{APP_ID}/public/data/sessions/*` and update frontend queries accordingly.

For beginners, Option 1 is simpler and matches the docs (`ARCHITECTURE.md`, `tech-spec-epic-E01.md`).

## Step 4 — Seed the `frameworks` collection

- Use `scripts/setup_framework_embeddings.py` to populate `frameworks` with `{name, description, embedding}`.
- Verify documents using Firebase Console or Firestore Studio (data explorer) to ensure embeddings exist.

## Step 5 — Frontend Pages and Components (MVP)

Build these in order to deliver a complete flow:

1) Authentication
- `/signup` and `/login` with Firebase Auth
- On signup success, create a `users/{uid}` document with `{ user_id: uid, sessions: [] }`

2) Dashboard (`/dashboard`)
- Shows metrics from `users/{uid}.sessions[]`:
  - Total decisions
  - Average confidence
  - Most used frameworks (bar chart)
  - Total LLM cost
- Prevents starting a new analysis if any `sessions` item has `status = 'InProgress'`

3) Start Decision (`/new`)
- Form to enter a decision query (`query`)
- On submit: create a new `sessions/{session_id}` with `{ user_id, query, status: 'Created' }`
- Immediately trigger Orchestrator (see Step 7) to perform ranking; then listen for updates in Firestore.

4) Framework Selection
- Display `ranked_frameworks` from session doc and allow selecting 4
- Write selection via Orchestrator tool or directly set `selected_frameworks` in Firestore if backend expects it there

5) Q&A
- For agents with `qa_state[agent].status === 'NEED_INFO'`, show one question at a time per agent
- Write answers back to Firestore (`qa_state`) using the Orchestrator tool (recommended) and await `ALL_AGENTS_READY`

6) Final Analysis & Synthesis
- After `execute_final_analysis_pass2`, display `agent_reports`
- Show `final_recommendation` and `confidence_score`
- Append summary to `users/{uid}.sessions[]`

7) History & Details
- `/history`: list `users/{uid}.sessions[]` summaries
- `/history/[sessionId]`: pull `sessions/{sessionId}` and show detailed `agent_reports` (see `stories/story-2.7.md`)

Page scaffolding matches acceptance criteria in `tech-spec-epic-E01.md`.

## Step 6 — Firestore Client Usage Patterns

- Read `frameworks`: `getDocs(collection(db, 'frameworks'))`
- Read user doc: `getDoc(doc(db, 'users', uid))`
- Read session doc: `onSnapshot(doc(db, 'sessions', sessionId), ...)` for real-time UI updates
- Write session doc: `setDoc(doc(db, 'sessions', sessionId), { ... }, { merge: true })`

Tip: Prefer `onSnapshot` for session UI to reflect live changes made by Orchestrator.

## Step 7 — Invoke the Orchestrator (Cloud Run)

- The Orchestrator service is launched via ADK `web` (`CMD ["adk","web","--host","0.0.0.0","--port","8080"]`). The standard endpoint is `/run` for agents.
- Expose the Orchestrator Cloud Run URL via env:

```
NEXT_PUBLIC_ORCHESTRATOR_URL=https://<orchestrator-service-url>
```

- Typical request shape to start ranking (payload may vary by ADK version — check your service logs):

```ts
await fetch(`${process.env.NEXT_PUBLIC_ORCHESTRATOR_URL}/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: {
      action: 'rank_frameworks',
      query,
      session_id,
      user_id: uid,
    }
  })
});
```

- After selection, trigger pass 1:

```ts
await fetch(`${process.env.NEXT_PUBLIC_ORCHESTRATOR_URL}/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: {
      action: 'invoke_framework_agents_pass1',
      session_id,
    }
  })
});
```

- To post answers in the Q&A loop:

```ts
await fetch(`${process.env.NEXT_PUBLIC_ORCHESTRATOR_URL}/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: {
      action: 'manage_per_agent_qa_loop',
      session_id,
      agent_name,
      answer,
    }
  })
});
```

- Final analysis and save recommendation similarly call `execute_final_analysis_pass2` and `save_final_recommendation`.

Note: The orchestrator tools write data to Firestore (e.g., `ranked_frameworks`, `qa_state`, `agent_reports`, `final_recommendation`) — your UI should read these live from `sessions/{session_id}`.

## Step 8 — Environment Variables for Agent URLs (backend)

- Orchestrator resolves each agent tool to `/run` with either local ports or deployed URLs via env, e.g.:
  - `PROS_CONS_AGENT_URL`, `SWOT_AGENT_URL`, `COST_BENEFIT_AGENT_URL`, `WEIGHTED_MATRIX_AGENT_URL`, `FIVE_WHYS_AGENT_URL`, `DECIDE_MODEL_AGENT_URL`, `TEN_TEN_TEN_AGENT_URL`, `RATIONAL_DECISION_MAKING_AGENT_URL`, `KEPNER_TREGOE_AGENT_URL`, `FIVE_WS_AND_H_AGENT_URL`
- Ensure these are set in the Cloud Run service environment for the Orchestrator.

## Step 9 — UX and Flow Details

- Follow `docs/ai-frontend-designer-prompt.md` and `docs/ux-design-specification.md` for the journey:
  - Landing → Decision input → Framework ranking & selection → Per-agent Q&A → Synthesis → Results → History
- Implement a two-tier global navigation and consistent layout.

## Step 10 — Testing

- Unit tests: form validation and Firestore data transforms
- Component tests: selection grid, Q&A panels, dashboard widgets
- E2E tests (Cypress): signup/login, start session, selection, Q&A, view results
- Use Firebase Emulator Suite for local Auth/Firestore testing when possible

## Step 11 — Deployment

Option A (Cloud Run, aligns with architecture docs):
- Build Next.js app as a container, deploy to Cloud Run
- Use Firebase Authentication and Firestore client SDK from the browser
- Configure service URL envs in Cloud Run for the Orchestrator

Option B (Firebase App Hosting, easier with Firebase Studio):
- From Firebase Studio, publish to App Hosting for fast iteration [Firebase Studio docs](https://firebase.google.com/docs/studio)
- Keep backend agents on Cloud Run; set `NEXT_PUBLIC_ORCHESTRATOR_URL` accordingly

## Common Pitfalls and Fixes

- Firestore security rules block reads/writes: verify `request.auth.uid` matches `user_id` in your docs
- Orchestrator writes under `artifacts/{APP_ID}/public/data/sessions/*`: either update `tools.py` to use top-level `sessions` or adjust your frontend queries and rules
- CORS errors calling Cloud Run: enable CORS or proxy via Next.js API routes
- Missing agent URLs: ensure all `*_AGENT_URL` envs are set on Orchestrator service

## Milestones (Follow in order)

1. Enable Firebase Auth and Firestore; add client config to `.env.local`
2. Build `/signup`, `/login`, and auth guard
3. Seed `frameworks` and render framework library
4. Dashboard with metrics from `users/{uid}.sessions[]`
5. New session flow: create `sessions/{session_id}` and call Orchestrator to rank
6. Framework selection UI; persist selection
7. Q&A loop UI; post answers; wait for `ALL_AGENTS_READY`
8. Final analysis; show `agent_reports`; show `final_recommendation`
9. History pages; deep session view (`agent_reports` per agent)
10. Deploy (Cloud Run or Firebase App Hosting)

---

Notes and Sources:
- Architecture and data model: `docs/ARCHITECTURE.md`
- Auth and dashboard acceptance criteria: `docs/tech-spec-epic-E01.md`
- Orchestrator tools and Firestore fields: `services/orchestrator/app/tools.py`
- Firebase Studio overview: https://firebase.google.com/docs/studio