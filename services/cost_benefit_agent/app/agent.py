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

FRAMEWORK_NAME = 'cost_benefit'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base() -> str:
    """
    Loads the knowledge base for the Cost-Benefit Analysis framework.

    Returns:
        str: The content of the knowledge base file.
    
    Raises:
        FileNotFoundError: If the knowledge base file is not found.
    """
    # Construct the path to the knowledge base file
    # This approach is robust to different operating systems
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
You are an expert AI agent specializing in the **Cost-Benefit Analysis** framework.
Your mission is to provide a detailed and unbiased evaluation of a decision by quantifying its costs and benefits.

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
- **Task:** Determine if you have enough information to perform a complete Cost-Benefit Analysis.
- **Output:**
  - If YES, return: `{{"status": "READY", "questions": []}}`
  - If NO, generate up to 3 critical questions to gather necessary financial and qualitative data, and return:
    `{{"status": "NEED_INFO", "questions": ["Question 1?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
- **Input:** `shared_context` (including `qa_answers`)
- **Task:** Perform the final, in-depth analysis.
- **Rules:**
  - You are PROHIBITED from asking more questions.
  - Use all available information (original query and all answers) to conduct the most thorough analysis possible.
  - Provide quantitative estimates where possible, using the '$' sign for clarity.
  - If critical information is still missing, you MUST include a `caveat` field in your final report explaining the gap and its impact on the analysis.
- **Output:** A JSON object containing the full analysis, structured as follows:
  `{{"costs": [ {{"item": "...", "cost_usd": 0, "description": "..."}} ], "benefits": [ {{"item": "...", "benefit_usd": 0, "description": "..."}} ], "net_value": 0, "recommendation": "...", "caveat": "..."}}`
"""

def get_agent() -> LlmAgent:
    """
    Builds and returns the Cost-Benefit Analysis Agent.

    This agent is configured with a specific prompt, model, and knowledge base
    to perform a detailed cost-benefit analysis based on user queries.

    Returns:
        LlmAgent: An instance of the LlmAgent configured for Cost-Benefit Analysis.
    """
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent that performs a detailed Cost-Benefit Analysis. It identifies, quantifies, and compares the costs and benefits of a decision to determine its net value and provide a clear recommendation.",
        tools=[]
    )