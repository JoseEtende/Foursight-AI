import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

load_dotenv()

if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'weighted_matrix'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base():
    """Loads the knowledge base for Weighted Matrix Analysis."""
    try:
        base_path = Path(__file__).parent.parent.parent.parent
        path = base_path / 'scripts' / 'framework_descriptions' / f'{FRAMEWORK_NAME}.md'
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
        return f"Error: Knowledge base file for {FRAMEWORK_NAME} analysis not found."

PROMPT_TEMPLATE = """
You are an expert AI agent specializing in the **Weighted Decision Matrix** framework.
Your mission is to evaluate options against weighted criteria, compute scores, and recommend the winning choice.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single JSON object.

**PASS 1: Information Sufficiency Analysis**
If you receive only an `original_query`, your task is to determine if you have enough information to define the options, criteria, and weights necessary for a complete Weighted Decision Matrix analysis.
- If YES, you MUST return the following JSON object:
  `{\{\"status\": \"SUFFICIENT\", "questions": []}}`
- If NO, you MUST generate up to 3 critical questions to identify options, define evaluation criteria, and understand their relative importance (weights) and return the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question 1?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
If you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis.
- You are PROHIBITED from asking more questions.
- Use all available information (the original query and all answers) to construct the matrix, assign weights (totaling 100), score each option against the criteria (0-10), and calculate the final weighted scores.
- If you determine that critical information is still missing, you MUST generate a `caveat` field in your final report explaining the gap and its impact.
- Your final output MUST be a JSON object containing the full analysis, formatted as structured lists of criteria and options scores, plus the winning option, final recommendation, and caveat:
  `{{"criteria": [ {{"name": "...", "weight": 0, "description": "..."}} ], "options_scores": [ {{"option": "...", "score": 0, "breakdown": "..."}} ], "winning_option": "...", "recommendation": "...", "caveat": "..."}}`
"""

def get_agent():
    """Builds and returns the Weighted Decision Matrix Agent."""
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent that performs a multi-criteria Weighted Decision Matrix analysis to evaluate and compare options. It scores choices against weighted criteria to provide a quantitative recommendation.",
        tools=[]
    )
