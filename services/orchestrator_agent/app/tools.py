import os
import random
import json
from typing import List, Dict, Any
import google.generativeai as genai
from .firebase_config import db

# --- Initialization & Setup ---

# Configure Generative AI client
try:
    if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
        os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    llm = genai.GenerativeModel('gemini-2.5-pro')
except KeyError:
    print("Warning: GOOGLE_API_KEY or GEMINI_API_KEY not set. LLM-based ranking will not work.")
    llm = None

# --- Multi-Criteria Ranking Implementation ---

def _analyze_query_characteristics(query: str) -> Dict[str, Any]:
    """
    Uses an LLM to analyze the user's query and extract key characteristics
    relevant to selecting a decision-making framework.
    """
    if not llm:
        return {"error": "LLM not configured"}

    prompt = f"""
    Analyze the following user query to determine the characteristics of the decision they are trying to make.
    Respond with a JSON object with the following keys:
    - "complexity": (string) Is the problem "low", "medium", or "high" complexity?
    - "data_availability": (string) Does the user seem to have "readily_available_data", "some_data", or "limited_data"?
    - "time_sensitivity": (string) Is the decision "time_sensitive", "moderate_urgency", or "not_time_sensitive"?
    - "quantitative_need": (string) Does the decision require "heavy_quantitative_analysis", "some_quantitative_analysis", or "mostly_qualitative_analysis"?
    - "stakeholder_involvement": (string) Does the decision involve "multiple_stakeholders", "few_stakeholders", or is it an "individual_decision"?
    - "strategic_operational": (string) Is the decision "strategic" (long-term, high-impact) or "operational" (short-term, process-oriented)?

    User Query: "{query}"
    """
    try:
        response = llm.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        clean_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error analyzing query with LLM: {e}")
        return {"error": "Failed to analyze query characteristics"}

def _calculate_criteria_scores(framework: Dict[str, Any], query_analysis: Dict[str, Any], query_embedding: List[float]) -> Dict[str, float]:
    """Calculates scores for each criterion based on query analysis and framework properties."""
    # This is a simplified scoring logic. A real implementation would have more nuanced rules.
    scores = {
        'semantic_relevance': sum(q * f for q, f in zip(query_embedding, framework.get('embedding', []))),
        'complexity_match': 1.0 if query_analysis.get('complexity') in framework.get('complexity', []) else 0.2,
        'data_availability': 1.0 if query_analysis.get('data_availability') in framework.get('data_focus', []) else 0.3,
        'time_sensitivity': 1.0 if query_analysis.get('time_sensitivity') in framework.get('speed', []) else 0.4,
        'quantitative_need': 1.0 if query_analysis.get('quantitative_need') in framework.get('type', []) else 0.5,
        'stakeholder_involvement': 1.0 if query_analysis.get('stakeholder_involvement') in framework.get('stakeholders', []) else 0.6,
        'strategic_operational': 1.0 if query_analysis.get('strategic_operational') in framework.get('focus', []) else 0.7,
    }
    return scores

def rank_frameworks(query: str) -> List[Dict[str, Any]]:
    """
    Ranks decision-making frameworks using a multi-criteria algorithm, including
    semantic relevance and LLM-based analysis of the query's characteristics.
    """
    print(f"Executing multi-criteria rank_frameworks for query: {query}")

    # 1. Generate Query Embedding
    try:
        query_result = genai.embed_content(model="models/text-embedding-004", content=query, task_type="RETRIEVAL_QUERY")
        query_embedding = query_result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}. Cannot perform semantic ranking.")
        query_embedding = []

    # 2. Analyze Query Characteristics with LLM
    query_analysis = _analyze_query_characteristics(query)
    if "error" in query_analysis:
        print("Falling back to simple semantic search due to LLM analysis failure.")
        # Simplified fallback logic can be placed here if needed
        return []

    # 3. Load frameworks from Firestore (they should have metadata for scoring)
    all_frameworks = []
    try:
        if db:
            frameworks_ref = db.collection('frameworks')
            for doc in frameworks_ref.stream():
                all_frameworks.append(doc.to_dict() or {})
        else:
            raise ConnectionError("Firestore client not available.")
    except Exception as e:
        print(f"Error loading frameworks from Firestore: {e}. Cannot rank.")
        return []

    # 4. Calculate Weighted Scores for each Framework
    weights = {
        'semantic_relevance': 0.10, 'complexity_match': 0.20, 'data_availability': 0.15,
        'time_sensitivity': 0.15, 'quantitative_need': 0.15, 'stakeholder_involvement': 0.15,
        'strategic_operational': 0.10
    }
    
    ranked_list = []
    for framework in all_frameworks:
        if not framework.get('embedding') and query_embedding:
            continue # Skip if embedding is required but missing

        criteria_scores = _calculate_criteria_scores(framework, query_analysis, query_embedding)
        
        total_score = sum(criteria_scores[key] * weights[key] for key in weights)
        
        framework['score'] = total_score
        ranked_list.append(framework)

    # 5. Sort by final score
    ranked_list.sort(key=lambda x: x['score'], reverse=True)

    print(f"Successfully ranked {len(ranked_list)} frameworks using multi-criteria algorithm.")
    return ranked_list
