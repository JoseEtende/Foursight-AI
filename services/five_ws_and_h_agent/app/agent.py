import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

load_dotenv()

if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'five_ws_and_h'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base():
    """Loads the knowledge base for the Five Ws and H analysis framework."""
    try:
        # Construct path to the knowledge base file
        base_path = Path(__file__).parent.parent.parent
        path = base_path / 'scripts' / 'framework_descriptions' / f'{FRAMEWORK_NAME}.md'

        # Fallback path for deployment environment
        if not path.exists():
            fallback = Path('/scripts/framework_descriptions') / f'{FRAMEWORK_NAME}.md'
            path = fallback
            logger.info(f"Using fallback knowledge base path: {fallback}")

        with open(path, 'r', encoding='utf-8') as f:
            kb = f.read()
            logger.info(f"Loaded knowledge base from {path} (chars={len(kb)})")
            return kb
    except FileNotFoundError:
        logger.error(f"Knowledge base file for {FRAMEWORK_NAME} not found at expected paths.")
        return f"Error: Knowledge base file for {FRAMEWORK_NAME} not found. Please ensure the file is in the correct directory."

PROMPT_TEMPLATE = """
You are an expert AI agent specializing in the **Five Ws and H (Who, What, Where, When, Why, How)** framework for comprehensive situational analysis.
Your mission is to clarify every W and H dimension of the situation and synthesize a concise, actionable plan.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles, ensuring every component is clearly and thoroughly addressed.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single, valid JSON object.

**PASS 1: Information Sufficiency Analysis**
When you receive an `original_query`, your primary task is to determine if you have enough information to fully address the Who, What, Where, When, Why, and How of the situation or decision.

- If the information is sufficient, you MUST return the following JSON object:
  `{\{\"status\": \"SUFFICIENT\", "questions": []}}`

- If the information is insufficient, you MUST generate up to 3 critical questions focusing on the most ambiguous or undefined W or H elements. Your response MUST be the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question about the 'Who' or 'How'?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
When you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis. At this stage, you are PROHIBITED from asking additional questions.

- Use all available information (the original query and all subsequent answers) to provide a comprehensive and structured breakdown for each of the six elements (Who, What, Where, When, Why, How).
- Conclude your analysis with a synthesized action plan that logically follows from the breakdown.
- If you determine that critical information is still missing despite the Q&A, you MUST include a `caveat` field in your final report. This caveat should explain the information gap and its potential impact on the analysis.
- Your final output MUST be a JSON object structured as follows:
  `{{"who": "...", "what": "...", "where": "...", "when": "...", "why": "...", "how": "...", "summary_action_plan": "...", "caveat": "(Optional) A statement about any remaining information gaps."}}`
"""

def get_agent():
    """
    Builds and returns the Five Ws and H Agent.

    This agent is designed to perform a comprehensive situational analysis using the Five Ws and H framework.
    It operates in two passes:
    1.  **Information Sufficiency Analysis**: Determines if the initial query provides enough information to proceed.
    2.  **Final Analysis**: Conducts the Five Ws and H investigation based on the provided context and returns a structured analysis.
    """
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent for performing comprehensive situational analysis using the Five Ws and H (Who, What, Where, When, Why, How) framework.",
        tools=[]
    )
