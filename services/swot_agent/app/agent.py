import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This will load the .env file from the root of the project
load_dotenv()

# ADK framework looks for 'GOOGLE_API_KEY'.
if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']
# --- End Environment Loading ---


def load_knowledge_base():
    """Loads the knowledge base from the swot.md file."""
    # Construct the path to the knowledge base file
    try:
        # Path is relative to the project root
        base_path = Path(__file__).parent.parent.parent.parent
        path = base_path / 'scripts' / 'framework_descriptions' / 'swot.md'
        if not path.exists():
            # Fallback for different deployment structure
            path = Path('/scripts/framework_descriptions/swot.md')
        
        with open(path, 'r', encoding='utf-8') as f:
            kb = f.read()
            # Setup logging once here to avoid global conflicts
            LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
            if not logging.getLogger().handlers:
                logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logger = logging.getLogger('FrameworkAgent.swot')
            logger.info(f"Loaded knowledge base from {path} (chars={len(kb)})")
            return kb
    except FileNotFoundError:
        return "Error: Knowledge base file for SWOT Analysis not found."


# The operational wrapper prompt that gives the agent its commands
PROMPT_TEMPLATE = """
You are an expert AI agent specializing in the **SWOT Analysis** framework.
Your mission is to evaluate internal strengths/weaknesses and external opportunities/threats, then propose a clear strategy.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must adhere strictly to its methodologies and principles.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single JSON object.

**PASS 1: Information Sufficiency Analysis**
If you receive only an `original_query`, your task is to determine if you have enough information to perform a complete SWOT analysis.
- If YES, you MUST return the following JSON object:
  `{{"status": "READY", "questions": []}}`
- If NO, you MUST generate up to 3 critical questions to gather the necessary information and return the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question 1?", "Question 2?", "..."]}}`

**PASS 2: Final Analysis**
If you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis.
- You are PROHIBITED from asking more questions.
- Use all available information (the original query and all answers) to conduct the most thorough analysis possible.
- If you determine that critical information is still missing, you MUST generate a `caveat` field in your final report explaining the gap and its impact.
- Your final output MUST be a JSON object containing the full analysis, formatted for the four SWOT quadrants plus a final recommendation and caveat:
  `{{"strengths": ["...", "..."], "weaknesses": ["...", "..."], "opportunities": ["...", "..."], "threats": ["...", "..."], "recommendation": "...", "caveat": "..."}}`
"""


def get_agent():
    """Builds and returns the SWOT Framework Agent."""
    
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logging.getLogger('FrameworkAgent.swot').info(f"Rendering prompt for swot (chars={len(final_prompt)})")
    
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent that performs a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis to evaluate a subject's strategic position. It identifies internal and external factors to provide a comprehensive overview and strategic recommendations.",
        tools=[]  # Framework agents have no tools
    )