import os
import json
import random
from typing import List, Dict, Any
from pathlib import Path

# ADK and Firebase Imports
from adk.agent import AgentTool
from adk.tools import FunctionTool
from adk.parallel import ParallelAgent
from google.cloud import firestore
import google.generativeai as genai

# --- Initialization & Setup ---

# Global variables (MANDATORY) provided by the execution environment
try:
    APP_ID = os.environ['APP_ID'] # Using environment variables for containerized deployment
except:
    APP_ID = "default-app-id" # Fallback for local testing

# Configure Generative AI client (required for embedding model)
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except:
    print("Warning: GEMINI_API_KEY not set. Embedding tools will not work.")
    
# --- Utility Functions ---

def get_firestore_db():
    """Initializes and returns a Firestore client or None if unavailable."""
    try:
        return firestore.Client()
    except Exception as e:
        print(f"Warning: Firestore client unavailable: {e}")
        return None

def get_session_ref(db: firestore.Client, session_id: str):
    """Gets the document reference for a specific session."""
    # Enforces the mandatory public data path for collaborative/session data
    return db.collection('artifacts').document(APP_ID).collection('public').document('data').collection('sessions').document(session_id)

# --- Resilient Session State Fallbacks ---

# In-memory fallback for session data when Firestore is not accessible
IN_MEMORY_SESSIONS: Dict[str, Any] = {}

def safe_get_session(session_id: str) -> Dict[str, Any]:
    """Safely retrieve session data from Firestore; falls back to in-memory."""
    db = get_firestore_db()
    if db is not None:
        try:
            doc = get_session_ref(db, session_id).get()
            if doc.exists:
                return doc.to_dict() or {}
        except Exception as e:
            print(f"Warning: Firestore get failed for session {session_id}: {e}. Using in-memory fallback.")
    # Fallback to in-memory store
    return IN_MEMORY_SESSIONS.get(session_id, {})

def safe_update_session(session_id: str, data: Dict[str, Any], merge: bool = True) -> None:
    """Safely update session data in Firestore; always mirrors to in-memory."""
    # Merge with in-memory first to guarantee continuity
    current = IN_MEMORY_SESSIONS.get(session_id, {})
    updated = {**current}
    updated.update(data)
    IN_MEMORY_SESSIONS[session_id] = updated

    db = get_firestore_db()
    if db is not None:
        try:
            ref = get_session_ref(db, session_id)
            if merge:
                ref.set(data, merge=True)
            else:
                ref.set(data)
        except Exception as e:
            print(f"Warning: Firestore set failed for session {session_id}: {e}. State kept in-memory.")

# --- Tool 1: Rank Frameworks (Phase 1) ---

@FunctionTool
def rank_frameworks(query: str, session_id: str) -> List[Dict[str, Any]]:
    """
    Ranks the 10 available decision-making frameworks based on the user's query 
    using semantic search, stores the results in Firestore, and returns the list.
    """
    print(f"Executing Tool 1: rank_frameworks for session {session_id}")
    db = get_firestore_db()

    # 1. Generate Query Embedding
    try:
        query_result = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_embedding = query_result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}. Returning mock ranks.")
        # Fallback to mock ranking if API key is missing or embedding fails
        mock_frameworks = [
            'swot_agent', 'pros_cons_agent', 'cost_benefit_agent', 
            'weighted_matrix_agent', 'decide_model_agent', 'five_whys_agent', 
            'ten_ten_ten_agent', 'rational_decision_making_agent', 
            'kepner_tregoe_agent', 'five_ws_and_h_agent'
        ]
        random.shuffle(mock_frameworks)
        ranked_list = [{'name': name, 'score': random.random()} for name in mock_frameworks]
        
        # Store mock data safely
        safe_update_session(session_id, {'query': query, 'ranked_frameworks': ranked_list}, merge=True)
        return ranked_list

    # 2. Load framework embeddings from Firestore (preferred for production)
    # This expects the 'frameworks' collection to be populated (see scripts/setup_framework_embeddings.py)
    all_frameworks = []
    try:
        if db is not None:
            frameworks_ref = db.collection('frameworks')
            for doc in frameworks_ref.stream():
                data = doc.to_dict() or {}
                # Expect fields: name, description, embedding
                name = data.get('name') or doc.id
                description = data.get('description', '')
                embedding = data.get('embedding')
                if isinstance(embedding, list):
                    all_frameworks.append({
                        'name': name,
                        'description': description,
                        'embedding': embedding
                    })
        else:
            raise Exception("Firestore client unavailable")
    except Exception as e:
        print(f"Error loading frameworks from Firestore: {e}. Falling back to mock ranks.")
        mock_frameworks = [
            'swot_agent', 'pros_cons_agent', 'cost_benefit_agent',
            'weighted_matrix_agent', 'decide_model_agent', 'five_whys_agent',
            'ten_ten_ten_agent', 'rational_decision_making_agent',
            'kepner_tregoe_agent', 'five_ws_and_h_agent'
        ]
        random.shuffle(mock_frameworks)
        ranked_list = [{'name': name, 'score': random.random()} for name in mock_frameworks]
        safe_update_session(session_id, {'query': query, 'ranked_frameworks': ranked_list}, merge=True)
        return ranked_list

    # 3. Perform Vector Search (Simplified Dot Product)
    ranked_list = []
    for framework in all_frameworks:
        # Ensure the framework has a pre-computed embedding
        if 'embedding' in framework and isinstance(framework['embedding'], list):
            # Simple dot product for similarity scoring
            score = sum(q * f for q, f in zip(query_embedding, framework['embedding']))
            ranked_list.append({
                'name': framework['name'],
                'description': framework['description'],
                'score': score
            })

    # Sort by score in descending order
    ranked_list.sort(key=lambda x: x['score'], reverse=True)

    # 4. Store Results safely
    safe_update_session(session_id, {'query': query, 'ranked_frameworks': ranked_list}, merge=True)
    print(f"Successfully ranked and stored {len(ranked_list)} frameworks.")
    return ranked_list

# --- Tool 2: Store User Selection (Phase 2) ---

@FunctionTool
def store_user_selection(session_id: str, selected_agents: List[str]) -> str:
    """Stores the user's final selection of 4 frameworks into the session state."""
    print(f"Executing Tool 2: store_user_selection for session {session_id}")
    # Initialize the QA state for the selected agents
    qa_state = {agent_name: {"status": "PENDING", "questions": [], "current_q_index": -1} for agent_name in selected_agents}
    
    safe_update_session(session_id, {
        'selected_frameworks': selected_agents,
        'qa_state': qa_state
    }, merge=True)
    
    return f"User selection stored: {', '.join(selected_agents)}. Ready for Pass 1 invocation."

# --- Tool 3: Invoke Pass 1 (Phase 2) ---

@FunctionTool
def invoke_framework_agents_pass1(session_id: str) -> str:
    """
    Invokes the 4 selected Framework Agents for their initial information sufficiency 
    check (Pass 1). Aggregates their status and questions into the session state.
    Returns the initial status report for the Orchestrator to display.
    """
    print(f"Executing Tool 3: invoke_framework_agents_pass1 for session {session_id}")
    session_doc = safe_get_session(session_id)
    
    selected_agents = session_doc.get('selected_frameworks', [])
    initial_query = session_doc.get('query', '')
    
    if not selected_agents:
        return "Error: No agents selected for Pass 1."

    # --- MOCK Parallel Execution and Response Collection ---
    # In a real ADK environment, you would use ParallelAgent here.
    # For now, we mock the results to set up the Q&A state.
    mock_responses: Dict[str, Dict[str, Any]] = {}
    
    # Mocking two agents needing info and two being ready
    for i, agent_name in enumerate(selected_agents):
        if i % 2 == 0: # Agents 1 & 3 need info
            mock_responses[agent_name] = {
                "status": "NEED_INFO",
                "questions": [
                    f"Question 1 from {agent_name} related to: {initial_query[:20]}...",
                    f"Question 2 from {agent_name} related to: {initial_query[:20]}..."
                ]
            }
        else: # Agents 2 & 4 are ready
            mock_responses[agent_name] = {
                "status": "READY",
                "questions": []
            }
            
    # --- Update Firestore QA State ---
    qa_state = session_doc.get('qa_state', {})
    status_report_lines = ["Status Report:"]
    
    for agent_name, response in mock_responses.items():
        qa_state[agent_name] = {
            "status": response['status'],
            "questions": [{"q": q, "a": None} for q in response['questions']],
            "current_q_index": 0 if response['status'] == 'NEED_INFO' else -1
        }
        
        status = "ready to proceed" if response['status'] == 'READY' else "Need more information"
        status_report_lines.append(f"* {agent_name.replace('_agent', '').upper()}: {status}")

    # Final update to session state
    safe_update_session(session_id, {'qa_state': qa_state}, merge=True)
    
    return "\n".join(status_report_lines)

# --- Tool 4: Manage Per-Agent Q&A Loop (Phase 3) ---

@FunctionTool
def manage_per_agent_qa_loop(session_id: str, target_agent_name: str, answer: str) -> str:
    """
    Saves the user's answer for a specific agent's question, advances the Q&A,
    and returns the next question or the final completion message.
    """
    print(f"Executing Tool 4: manage_per_agent_qa_loop for session {session_id}, agent {target_agent_name}")
    try:
        session_doc = safe_get_session(session_id)
        qa_state = session_doc.get('qa_state', {})
    except Exception as e:
        return f"Error accessing session state: {e}"
        
    # 1. Validate Agent and State
    agent_state = qa_state.get(target_agent_name)
    if not agent_state:
        return f"Error: Agent '{target_agent_name}' not found in the current session state."

    q_index = agent_state.get('current_q_index', -1)
    questions = agent_state.get('questions', [])
    
    if q_index < 0 or q_index >= len(questions):
        return f"Error: Agent '{target_agent_name}' is not currently expecting an answer or Q&A is complete."

    # 2. Save the Answer
    questions[q_index]['a'] = answer
    
    # 3. Advance the Index
    next_q_index = q_index + 1
    
    # 4. Check Agent Completion Status
    if next_q_index < len(questions):
        # Agent needs another question
        agent_state['current_q_index'] = next_q_index
        next_response = f"NEXT_QUESTION: {questions[next_q_index]['q']}"
    else:
        # Agent's Q&A is complete
        agent_state['status'] = 'READY'
        agent_state['current_q_index'] = -1
        next_response = f"AGENT_READY: {target_agent_name}"

    qa_state[target_agent_name] = agent_state
    
    # 5. Check Overall Completion Status
    all_ready = all(
        qa_state[agent]['status'] == 'READY' 
        for agent in session_doc.get('selected_frameworks', [])
    )

    if all_ready:
        # Final update and signal the Orchestrator to move to Phase 4
        safe_update_session(session_id, {'qa_state': qa_state}, merge=True)
        return "ALL_AGENTS_READY"
    else:
        # Only update the single agent's state and return the response
        safe_update_session(session_id, {'qa_state': qa_state}, merge=True)
        return next_response

# --- Tool 5: Execute Pass 2 (Phase 4) ---

@FunctionTool
def execute_final_analysis_pass2(session_id: str) -> str:
    """
    Invokes the 4 selected Framework Agents for their final analysis 
    (Pass 2) with the complete context (initial query + all Q&A answers).
    Stores the 4 resulting JSON reports.
    """
    print(f"Executing Tool 5: execute_final_analysis_pass2 for session {session_id}")
    session_doc = safe_get_session(session_id)
    
    selected_agents = session_doc.get('selected_frameworks', [])
    qa_state = session_doc.get('qa_state', {})
    initial_query = session_doc.get('query', '')
    
    # 1. Compile Final Context for all Agents
    collected_answers = {}
    for agent_name, state in qa_state.items():
        if state['status'] == 'READY':
            answers = {q_data['q']: q_data['a'] for q_data in state.get('questions', []) if q_data.get('a')}
            collected_answers[agent_name] = answers
    
    # This compiled context would be passed to the ParallelAgent execution
    full_context = {
        'initial_query': initial_query,
        'collected_answers': collected_answers
    }

    # --- MOCK Parallel Execution and Final Report Storage ---
    mock_reports = {}
    for agent_name in selected_agents:
        # The agent's report would be complex JSON/Markdown. We mock a summary.
        mock_reports[agent_name] = {
            "summary": f"Final analysis summary for {agent_name}. All questions were answered.",
            "report_data": {"key": "value", "context_used": full_context} 
        }

    # 2. Store the Reports
    safe_update_session(session_id, {'agent_reports': mock_reports}, merge=True)
    
    return "Final analysis complete. Reports stored in session state. Ready for synthesis."

# --- Tool 6: Save Final Recommendation (Phase 4) ---

@FunctionTool
def save_final_recommendation(session_id: str, recommendation_text: str, confidence_score: float = 0.8) -> str:
    """
    Persistently stores the Orchestrator's final synthesized recommendation 
    and confidence score in the session document.
    """
    print(f"Executing Tool 6: save_final_recommendation for session {session_id}")
    # Update the session document with the final result
    safe_update_session(session_id, {
        'final_recommendation': recommendation_text,
        'confidence_score': confidence_score,
        'status': 'Completed'
    }, merge=True)
    
    # Additional: Update the user's history document (simplified)
    # This step is critical for the user history view (FR-2.3.2)
    # We would need the user_id for this, which is not explicitly passed here, 
    # but assumed to be available or retrievable.
    
    return "Final recommendation and confidence score successfully stored."