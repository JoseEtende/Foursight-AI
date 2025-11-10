import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

load_dotenv()

if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'pros_cons'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base():
    """Loads the knowledge base for the Pros and Cons analysis framework."""
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
You are an expert AI agent specializing in the **Pros and Cons Analysis** framework.
Your mission is to weigh advantages and disadvantages comprehensively and recommend a clear course of action.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single, valid JSON object.

**PASS 1: Information Sufficiency Analysis**
When you receive an `original_query`, your primary task is to determine if you have enough information to perform a complete Pros and Cons analysis.

- If the information is sufficient, you MUST return the following JSON object:
  `{{"status": "READY", "questions": []}}`

- If the information is insufficient, you MUST generate up to 3 critical questions to gather the necessary information. Your response MUST be the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question 1?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
When you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis. At this stage, you are PROHIBITED from asking additional questions.

- Use all available information (the original query and all subsequent answers) to conduct the most thorough analysis possible.
- If you determine that critical information is still missing despite the Q&A, you MUST include a `caveat` field in your final report. This caveat should explain the information gap and its potential impact on the analysis.
- Your final output MUST be a JSON object containing the full analysis:
  `{{"pros": ["...List of advantages based on the context..."], "cons": ["...List of disadvantages based on the context..."], "recommendation": "...", "caveat": "(Optional) A statement about any remaining information gaps."}}`
"""

def get_agent():
    """
    Builds and returns the Pros and Cons Framework Agent.

    This agent is designed to facilitate a structured analysis of the advantages and disadvantages of a particular decision or course of action.
    It operates in two passes:
    1.  **Information Sufficiency Analysis**: Determines if the initial query provides enough information to proceed.
    2.  **Final Analysis**: Conducts the full Pros and Cons analysis based on the provided context and returns a structured report.
    """
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent for performing a structured Pros and Cons analysis to support decision-making.",
        tools=[]
    )