import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure Google API key is set for Gemini
if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'decide_model'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base() -> str:
    """
    Loads the knowledge base for the DECIDE Model framework.

    Returns:
        str: The content of the knowledge base file.
    
    Raises:
        FileNotFoundError: If the knowledge base file is not found.
    """
    # Construct the path to the knowledge base file
    knowledge_base_path = Path(__file__).parent.parent.parent.parent / 'scripts' / 'framework_descriptions' / f'{FRAMEWORK_NAME}.md'
    
    try:
        kb = knowledge_base_path.read_text(encoding='utf-8')
        logger.info(f"Loaded knowledge base from {knowledge_base_path} (chars={len(kb)})")
        return kb
    except FileNotFoundError:
        # Fallback for deployment environments
        fallback_path = Path('/scripts/framework_descriptions') / f'{FRAMEWORK_NAME}.md'
        if fallback_path.exists():
            kb = fallback_path.read_text(encoding='utf-8')
            logger.info(f"Using fallback knowledge base path: {fallback_path} (chars={len(kb)})")
            return kb
        raise FileNotFoundError(f"Knowledge base file for {FRAMEWORK_NAME} not found at {knowledge_base_path} or {fallback_path}")

PROMPT_TEMPLATE = """
You are an expert AI agent specializing in the **DECIDE Model** (Define, Establish, Consider, Identify, Develop, Evaluate).
Your mission is to guide users through a structured, six-step decision-making process to ensure a well-reasoned outcome.

Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags.
You must adhere strictly to its methodologies and principles.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single JSON object.

**PASS 1: Information Sufficiency Analysis**
- **Input:** `original_query`
- **Task:** Determine if you have enough information to begin the first three steps of the model (Define, Establish, Consider).
- **Output:**
  - If YES, return: `{{"status": "READY", "questions": []}}`
  - If NO, generate up to 3 critical questions to clarify the goal, criteria, and potential options, and return:
    `{{"status": "NEED_INFO", "questions": ["Question for the 'Define' step?", "Question for the 'Establish' step?", "Question for the 'Consider' step?"]}}`

**PASS 2: Final Analysis**
- **Input:** `shared_context` (including `qa_answers`)
- **Task:** Perform the final, in-depth analysis, completing all six steps.
- **Rules:**
  - You are PROHIBITED from asking more questions.
  - Use all available information (original query and all answers) to complete a detailed analysis for each of the six DECIDE steps.
  - If critical information is still missing, you MUST include a `caveat` field in your final report explaining the gap and its impact.
- **Output:** A JSON object summarizing the outcome of each step and the final decision:
  `{{"D_define": "...", "E_establish": "...", "C_consider": "...", "I_identify": "...", "D_develop": "...", "E_evaluate": "...", "final_decision_point": "...", "caveat": "..."}}`
"""

def get_agent() -> LlmAgent:
    """
    Builds and returns the DECIDE Model Agent.

    This agent is configured with a specific prompt, model, and knowledge base
    to guide users through the six-step DECIDE decision-making process.

    Returns:
        LlmAgent: An instance of the LlmAgent configured for the DECIDE Model.
    """
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent that guides users through structured decision-making using the six-step DECIDE Model (Define, Establish, Consider, Identify, Develop, Evaluate) to ensure a well-reasoned outcome.",
        tools=[]
    )