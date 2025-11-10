import os
import logging
import json
from typing import AsyncGenerator, List, Dict, Any

from adk.agent import BaseAgent, LlmAgent, AgentTool, ParallelAgent
from adk.agents.invocation_context import InvocationContext
from adk.events import Event, UIMessage
from . import tools

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Framework Agent Definitions ---
def create_framework_agent_tools() -> List[AgentTool]:
    """
    Creates and returns a list of AgentTool instances for all 10 framework agents,
    relying exclusively on environment variables for service URLs.
    """
    frameworks = [
        ("pros_cons_agent", "A specialized agent for performing a Pros and Cons analysis."),
        ("swot_agent", "A specialized agent for performing a SWOT analysis."),
        ("cost_benefit_agent", "A specialized agent for a Cost-Benefit analysis."),
        ("weighted_matrix_agent", "A specialized agent for creating a Weighted Matrix to evaluate options."),
        ("five_whys_agent", "A specialized agent for root-cause analysis using the 5 Whys technique."),
        ("five_ws_and_h_agent", "A specialized agent for defining a situation using the 5 W's and H framework."),
        ("ten_ten_ten_agent", "A specialized agent for evaluating decisions using the 10-10-10 Rule."),
        ("decide_model_agent", "A specialized agent for structured decision-making using the DECIDE Model."),
        ("kepner_tregoe_agent", "A specialized agent for systematic problem analysis using the Kepner-Tregoe method."),
        ("rational_decision_making_agent", "A specialized agent for formalized, logical Rational Decision Making.")
    ]
    
    agent_tools = []
    for name, description in frameworks:
        url_env_var = f"{name.upper()}_URL"
        agent_url = os.environ.get(url_env_var)
        
        if agent_url:
            agent_tools.append(AgentTool(
                name=name,
                description=description,
                url=f"{agent_url}/run"
            ))
        else:
            logger.warning(f"Environment variable {url_env_var} not set. The '{name}' agent will be unavailable.")
            
    return agent_tools

# --- Helper Functions for Q&A ---
def _initialize_qa_state(ctx: InvocationContext):
    """Reads Pass 1 results and sets up the initial state for the Q&A session."""
    qa_state = {"agents_with_questions": [], "completed_agents": [], "current_question": None, "answers": {}}
    selected_agents = ctx.session.state.get("selected_frameworks", [])
    
    for agent_name in selected_agents:
        # ADK's ParallelAgent stores the final response content of each sub-agent in the session state
        # with the agent's name as the key.
        result_str = ctx.session.state.get(agent_name, '{}')
        try:
            result = json.loads(result_str)
            if result.get("status") == "NEED_INFO" and result.get("questions"):
                qa_state["agents_with_questions"].append({
                    "name": agent_name,
                    "questions": result["questions"],
                    "question_index": 0
                })
                qa_state["answers"][agent_name] = []
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Could not parse result for {agent_name}: {result_str} - Error: {e}")

    ctx.session.state["qa_state"] = qa_state
    logger.info(f"Q&A state initialized: {qa_state}")

def _get_next_question(qa_state: Dict[str, Any]) -> Dict[str, Any] | None:
    """Finds the next agent with an unanswered question."""
    if not qa_state.get("agents_with_questions"):
        return None
    
    next_agent_to_ask = qa_state["agents_with_questions"][0]
    question_text = next_agent_to_ask["questions"][next_agent_to_ask["question_index"]]
    
    return {"agent_name": next_agent_to_ask["name"], "question": question_text}

# --- Custom Orchestrator Agent ---
class OrchestratorAgent(BaseAgent):
    """
    A custom agent that orchestrates the FourSight workflow using explicit Python code.
    """
    def __init__(self):
        self.framework_agent_tools = create_framework_agent_tools()
        self.framework_agents_map = {agent.name: agent for agent in self.framework_agent_tools}
        self.synthesis_agent = LlmAgent(
            name="SynthesisAgent", model="gemini-2.5-pro",
            instruction="You are a master analyst. Synthesize the reports from four different decision frameworks into a single, cohesive, and actionable recommendation. The reports will be in the session state key 'agent_reports'. Your output should follow the structure defined in the PRD."
        )
        super().__init__(name="Orchestrator", sub_agents=self.framework_agent_tools + [self.synthesis_agent])

    @classmethod
    def from_init_params(cls, **kwargs):
        return cls()

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Defines the explicit, code-driven workflow for FourSight.
        """
        # --- Check for ongoing Q&A session ---
        qa_state = ctx.session.state.get("qa_state")
        if qa_state and qa_state.get("current_question"):
            # If we are in a Q&A session, the user's message is an answer.
            last_message = ctx.session.history.get_last_message()
            answer = last_message.content.parts[0].text if last_message and last_message.content.parts else ""
            
            # Store the answer
            current_q_info = qa_state["current_question"]
            agent_name = current_q_info["agent_name"]
            qa_state["answers"][agent_name].append({"q": current_q_info["question"], "a": answer})
            
            # Find the agent we just answered for and advance its index
            for agent in qa_state["agents_with_questions"]:
                if agent["name"] == agent_name:
                    agent["question_index"] += 1
                    # If all questions for this agent are answered, move it to completed
                    if agent["question_index"] >= len(agent["questions"]):
                        qa_state["completed_agents"].append(agent)
                        qa_state["agents_with_questions"].pop(0)
                    break
            
            # Ask the next question or conclude
            next_question = _get_next_question(qa_state)
            if next_question:
                qa_state["current_question"] = next_question
                ctx.session.state["qa_state"] = qa_state
                yield UIMessage(f"Thank you. Next question from {next_question['agent_name']}:\n\n{next_question['question']}")
                return
            else:
                # Q&A is complete
                ctx.session.state["qa_state"] = qa_state
                yield UIMessage("Thank you. All questions have been answered. Proceeding to final analysis.")
                # Fall through to Phase 4
        
        # --- Start of Workflow ---
        if ctx.session.history.get_turn_count() > 1 and not qa_state:
             # Avoid re-running phase 1 on subsequent turns if not in Q&A
            return

        logger.info(f"[{self.name}] Starting workflow for session: {ctx.session.session_id}")
        initial_message = ctx.session.history.get_last_message()
        if not initial_message or not initial_message.content.parts:
            yield UIMessage("Hello! Please state your problem or goal to begin the analysis.")
            return

        query = initial_message.content.parts[0].text
        ctx.session.state["query"] = query
        
        # --- Phase 1: Ranking & Selection (Simplified) ---
        ranked_frameworks = tools.rank_frameworks(query)
        ctx.session.state["ranked_frameworks"] = ranked_frameworks
        top_4 = [f["name"] for f in ranked_frameworks[:4]]
        selected_agent_names = top_4 # Placeholder for user selection
        ctx.session.state["selected_frameworks"] = selected_agent_names
        yield UIMessage(f"Selection confirmed. Starting analysis with: {', '.join(selected_agent_names)}")

        # --- Phase 2: Pass 1 - Information Sufficiency Analysis ---
        selected_agents = [self.framework_agents_map[name] for name in selected_agent_names]
        pass1_invoker = ParallelAgent(name="Pass1Invoker", sub_agents=selected_agents)
        
        logger.info(f"[{self.name}] Invoking Pass 1 for {len(selected_agents)} agents in parallel.")
        async for event in pass1_invoker.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Pass 1 invocation complete.")

        # --- Phase 3: Interactive Q&A Setup ---
        _initialize_qa_state(ctx)
        qa_state = ctx.session.state["qa_state"]
        
        next_question = _get_next_question(qa_state)
        if next_question:
            qa_state["current_question"] = next_question
            ctx.session.state["qa_state"] = qa_state
            yield UIMessage(f"Initial analysis is complete. Some agents need more information to proceed.\n\nFirst question from {next_question['agent_name']}:\n\n{next_question['question']}")
            return
        else:
            yield UIMessage("Initial analysis is complete. All agents have sufficient information. Proceeding to final analysis.")
            # Fall through to Phase 4
            
        # --- Phase 4: Final Analysis & Synthesis ---
        logger.info(f"[{self.name}] Starting Phase 4: Final Analysis.")
        
        # 4a. Prepare the shared context for Pass 2
        shared_context = {
            "original_query": ctx.session.state.get("query", ""),
            "qa_answers": ctx.session.state.get("qa_state", {}).get("answers", {})
        }
        # The ADK automatically passes the session state, but we could also
        # explicitly pass this context if needed. For now, the agents are
        # designed to read from the shared session state.
        
        # 4b. Invoke agents for Pass 2 in parallel
        selected_agent_names = ctx.session.state.get("selected_frameworks", [])
        selected_agents = [self.framework_agents_map[name] for name in selected_agent_names]
        
        pass2_invoker = ParallelAgent(name="Pass2Invoker", sub_agents=selected_agents)
        
        logger.info(f"[{self.name}] Invoking Pass 2 for {len(selected_agents)} agents in parallel.")
        async for event in pass2_invoker.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Pass 2 invocation complete. All framework reports are in session state.")
        
        # 4c. Synthesize the final recommendation
        # The individual agent reports are now in the session state under their names.
        # We will now call the synthesis agent to create the final report.
        # The synthesis agent's prompt tells it to look for the reports in the state.
        
        logger.info(f"[{self.name}] Invoking Synthesis Agent.")
        async for event in self.synthesis_agent.run_async(ctx):
            # Yield the final synthesized response to the user
            yield event
            
        # The final response from the synthesis agent is the end of the workflow.
        # We can also save this to the state for history.
        final_recommendation = ctx.session.history.get_last_message()
        if final_recommendation:
            ctx.session.state["final_recommendation"] = final_recommendation.to_dict()

        logger.info(f"[{self.name}] Workflow complete.")


def get_agent():
    """Factory function required by ADK to get the root agent."""
    return OrchestratorAgent()
