import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

load_dotenv()

if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'ten_ten_ten'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base():
    """Loads the knowledge base for the 10-10-10 Analysis."""
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
You are an expert AI agent specializing in the **10-10-10 decision-making framework**.
Your mission is to assess impact across 10 minutes, 10 months, and 10 years, then synthesize a balanced recommendation.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must use this framework to assess the impact of a user's decision across three critical time horizons: 10 minutes, 10 months, and 10 years.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single JSON object.

**PASS 1: Information Sufficiency Analysis**
If you receive only an `original_query`, your task is to determine if you have enough information to clearly define the immediate decision and understand its context and stakes.
- If YES, you MUST return the following JSON object:
  `{{"status": "READY", "questions": []}}`
- If NO, you MUST generate up to 3 critical questions to clarify the core decision, the immediate feelings it might generate, and the long-term context, and return the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question about the immediate action?", "Question about the biggest challenge in 10 months?", "Question 3?", "..."]}}`

**PASS 2: Final Analysis**
If you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis.
- You are PROHIBITED from asking more questions.
- Use all available information (the original query and all answers) to detail the likely emotional/logistical impact at each time horizon. Conclude with a synthesized recommendation based on balancing these short-term and long-term consequences.
- If you determine that critical information is still missing, you MUST generate a `caveat` field in your final report explaining the gap and its impact.
- Your final output MUST be a JSON object containing the impact analysis and the synthesized recommendation:
  `{{"decision": "...", "impact_10_minutes": "...", "impact_10_months": "...", "impact_10_years": "...", "synthesized_recommendation": "...", "caveat": "..."}}`
"""

def get_agent():
    """Builds and returns the 10-10-10 Agent."""
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent that evaluates the short, medium, and long-term consequences of a decision using the 10-10-10 framework. It helps users gain perspective by considering the impact in 10 minutes, 10 months, and 10 years.",
        tools=[]
    )