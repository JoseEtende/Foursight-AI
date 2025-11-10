import os
import logging
from typing import List
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any

# ADK Core Imports
from adk.agent import LlmAgent, AgentTool
from adk.models import Model 
from adk.memory import ConversationHistory, InMemoryHistory # Imports for Memory

# Local Tool Imports (assuming these functions are in the sibling 'tools.py')
from . import tools 

# --- Load Environment Variables ---
load_dotenv()

# ADK framework looks for 'GOOGLE_API_KEY'.
# Let's set it from your 'GEMINI_API_KEY' if it's not already set.
if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']
# --- End Environment Loading ---

# --- 1. GLOBAL LOGGING SETUP (NFR-3.4 Observability) ---
# Centralized logging configuration. Note: The session ID will be injected dynamically below.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [ADK Session:%(session_id)s] %(message)s'
)
# Base logger for the orchestrator service
base_logger = logging.getLogger('OrchestratorService')


# --- 2. FRAMEWORK AGENT TOOL DEFINITIONS (Standard Proxies) ---

def create_framework_agent_tool(name: str, description: str, local_port: int, deployed_url: str = None) -> AgentTool:
    """Creates an AgentTool, using the deployed URL if available, otherwise localhost."""
    
    # In a real ADK system, this tool would represent the remote service endpoint.
    base_url = f"http://localhost:{local_port}"
    
    # Check if a deployed URL is explicitly set (e.g., via ENV var for production)
    if deployed_url:
        base_url = deployed_url
        
    return AgentTool(
        name=name,
        description=description,
        url=f"{base_url}/run" # Standard ADK '/run' endpoint for agents
    )

# 1. Pros and Cons Agent
pros_cons_agent = create_framework_agent_tool(
    name="pros_cons_agent",
    description="A specialized agent for performing a Pros and Cons analysis.",
    local_port=8001,
    deployed_url=os.environ.get("PROS_CONS_AGENT_URL")
)

# [... Tool definitions for the other 9 agents: SWOT, Cost-Benefit, etc. ...]
# We define the 10 agents as AgentTool instances, ready to be invoked by the Orchestrator's internal tools.

# 2. SWOT Agent
swot_agent = create_framework_agent_tool(
    name="swot_agent",
    description="A specialized agent for performing a SWOT analysis.",
    local_port=8002,
    deployed_url=os.environ.get("SWOT_AGENT_URL")
)

# 3. Cost-Benefit Agent
cost_benefit_agent = create_framework_agent_tool(
    name="cost_benefit_agent",
    description="A specialized agent for a Cost-Benefit analysis.",
    local_port=8003,
    deployed_url=os.environ.get("COST_BENEFIT_AGENT_URL")
)

# 4. Weighted Matrix Agent
weighted_matrix_agent = create_framework_agent_tool(
    name="weighted_matrix_agent",
    description="A specialized agent for creating a Weighted Matrix to evaluate options.",
    local_port=8004,
    deployed_url=os.environ.get("WEIGHTED_MATRIX_AGENT_URL")
)

# 5. Five Whys Agent
five_whys_agent = create_framework_agent_tool(
    name="five_whys_agent",
    description="A specialized agent for root-cause analysis using the 5 Whys technique.",
    local_port=8005,
    deployed_url=os.environ.get("FIVE_WHYS_AGENT_URL")
)

# 6. 5 Ws and H Agent
five_ws_and_h_agent = create_framework_agent_tool(
    name="five_ws_and_h_agent",
    description="A specialized agent for defining a situation using the 5 W's and H framework.",
    local_port=8006,
    deployed_url=os.environ.get("FIVE_WS_AND_H_AGENT_URL")
)

# 7. 10-10-10 Rule Agent
ten_ten_ten_agent = create_framework_agent_tool(
    name="ten_ten_ten_agent",
    description="A specialized agent for evaluating decisions using the 10-10-10 Rule.",
    local_port=8007,
    deployed_url=os.environ.get("TEN_TEN_TEN_AGENT_URL")
)

# 8. DECIDE Model Agent
decide_model_agent = create_framework_agent_tool(
    name="decide_model_agent",
    description="A specialized agent for structured decision-making using the DECIDE Model.",
    local_port=8008,
    deployed_url=os.environ.get("DECIDE_MODEL_AGENT_URL")
)

# 9. Kepner-Tregoe Agent
kepner_tregoe_agent = create_framework_agent_tool(
    name="kepner_tregoe_agent",
    description="A specialized agent for systematic problem analysis and decision making using the Kepner-Tregoe method.",
    local_port=8009,
    deployed_url=os.environ.get("KEPNER_TREGOE_AGENT_URL")
)

# 10. Rational Decision Making Agent
rational_decision_making_agent = create_framework_agent_tool(
    name="rational_decision_making_agent",
    description="A specialized agent for formalized, logical Rational Decision Making.",
    local_port=8010,
    deployed_url=os.environ.get("RATIONAL_DECISION_MAKING_AGENT_URL")
)


# --- 3. ORCHESTRATOR SYSTEM PROMPT (Workflow Logic) ---

# This is the primary prompt for the Orchestrator Agent.
# It guides the agent through a 4-phase process to help the user
# make a decision.

ORCHESTRATOR_PROMPT = """
You are the Orchestrator, a master decision-making assistant. Your goal is to guide the user through a structured, four-phase process to deconstruct their problem, analyze it with the best-suited mental models, and synthesize a final, actionable recommendation.

**Phase 1: Framework Ranking & Selection**
1.  **Understand the User's Goal:** The user will state their problem or goal.
2.  **Rank Frameworks:** Use the `rank_frameworks` tool to perform a semantic search and rank the 10 available decision-making frameworks based on their relevance to the user's query.
3.  **Present & Select:** Show the user the top 4-5 ranked frameworks with brief descriptions. Ask them to select the 3-4 they find most appealing.

**Phase 2: Initial Analysis (Pass 1)**
1.  **Store Selection:** Once the user confirms their choice, use the `store_user_selection` tool to save their selection.
2.  **Invoke Agents (Pass 1):** Use the `invoke_framework_agents_pass1` tool. This triggers the selected agents to perform their first analysis. Each agent will independently assess if it has enough information to proceed or if it needs to ask clarifying questions.

**Phase 3: Per-Agent Q&A**
1.  **Report Status:** The `invoke_framework_agents_pass1` tool will return a status for each agent (`READY` or `NEED_INFO`). Present this status to the user.
2.  **Manage Q&A:** For each agent that returned `NEED_INFO`, use the `manage_per_agent_qa_loop` tool. This tool will present one question at a time from an agent to the user.
3.  **Route Answers:** The tool will take the user's answer and send it back to the correct agent. This loop continues until all questions for all agents are answered. The tool will return `STATUS_ALL_AGENTS_READY` when the loop is complete.

**Phase 4: Final Analysis & Synthesis (Pass 2)**
1.  **Execute Final Analysis:** Once all agents are `READY`, use the `execute_final_analysis_pass2` tool. This invokes all selected agents to perform their final, in-depth analysis using the complete information.
2.  **Synthesize Recommendation:** The tool will return the final reports from all agents. Your final job is to synthesize these individual analyses into a single, cohesive, and actionable recommendation for the user.
3.  **Save Recommendation:** Use the `save_final_recommendation` tool to persist the final output to Firestore for the user to access later.
"""

# --- Tool Definitions ---
# The ADK automatically discovers and registers tools decorated with @FunctionTool.
# We are defining the tools in a separate `tools.py` file for better organization.
from . import tools 

# --- Agent Class ---

class OrchestratorAgent(LlmAgent):
    """
    The primary agent for the multi-agent system. It orchestrates the 
    workflow between the user and the specialized agents.
    """
    def __init__(self, session_id: str, user_id: str):
        super().__init__(
            agent_id="orchestrator_agent",
            agent_name="Orchestrator Agent",
            description="The primary agent for the multi-agent system. It orchestrates the workflow between the user and the specialized agents.",
            # Use the latest Gemini model for advanced reasoning
            model="gemini-2.5-pro",
            prompt=ORCHESTRATOR_PROMPT,
            # The tools are automatically discovered from the `tools.py` module
            available_tools=tools,
            # Use in-memory history for this session
            history=InMemoryHistory(session_id=session_id),
            # Enable contextual logging for this agent
            use_contextual_logging=True,
            session_id=session_id,
            user_id=user_id
        )


# --- 5. AGENT FACTORY FUNCTION ---

def get_orchestrator_agent(session_id: str, user_id: str) -> OrchestratorAgent:
    """Factory function to build and return the Orchestrator Agent with session context."""
    return OrchestratorAgent(session_id=session_id, user_id=user_id)