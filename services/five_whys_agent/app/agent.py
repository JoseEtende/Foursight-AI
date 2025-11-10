import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

load_dotenv()

if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'five_whys'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base():
    """Loads the knowledge base for the Five Whys analysis framework."""
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
You are an expert AI agent specializing in the **Five Whys** framework for root cause analysis.
Your mission is to uncover the most likely root cause via a rigorous five-"Why" chain and propose an actionable countermeasure.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles to ensure a complete and logical causal chain.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single, valid JSON object.

**PASS 1: Information Sufficiency Analysis**
When you receive an `original_query`, your primary task is to determine if you have enough information to clearly define the initial problem and begin the causal investigation.

- If the information is sufficient, you MUST return the following JSON object:
  `{{"status": "READY", "questions": []}}`

- If the information is insufficient, you MUST generate up to 3 critical questions to clarify the problem, understand the context, or gather details about the people and processes involved. Your response MUST be the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question 1 (e.g., to define the failure more precisely)?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
When you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis. At this stage, you are PROHIBITED from asking additional questions.

- Use all available information (the original query and all subsequent answers) to construct a detailed and logical chain of five 'Why?' statements. This chain must lead to the most likely root cause.
- Based on the root cause, you must propose a permanent and actionable countermeasure (recommendation).
- If you determine that critical information is still missing despite the Q&A, you MUST include a `caveat` field in your final report. This caveat should explain the information gap and its potential impact on the analysis.
- Your final output MUST be a JSON object structured as follows:
  `{{"problem": "...", "whys_chain": [ {{"why_number": 1, "question": "Why did X happen?", "answer": "Because of Y."}}, {{"why_number": 2, "question": "Why did Y happen?", "answer": "Because of Z."}}, ..., {{"why_number": 5, "question": "Why did P happen?", "answer": "Because of Q.", "is_root_cause": true}} ], "recommendation": "...", "caveat": "(Optional) A statement about any remaining information gaps."}}`
"""

def get_agent():
    """
    Builds and returns the Five Whys Agent.

    This agent is designed to perform root cause analysis using the Five Whys framework. It operates in two passes:
    1.  **Information Sufficiency Analysis**: Determines if the initial query provides enough information to proceed.
    2.  **Final Analysis**: Conducts the Five Whys investigation based on the provided context and returns a structured analysis.
    """
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent for performing root cause analysis using the Five Whys technique. It identifies the root cause of a problem by repeatedly asking 'Why?'.",
        tools=[]
    )