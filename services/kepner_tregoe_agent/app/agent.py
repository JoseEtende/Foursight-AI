import os
import logging
from pathlib import Path
from adk.agent import LlmAgent
from dotenv import load_dotenv

load_dotenv()

if 'GEMINI_API_KEY' in os.environ and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = os.environ['GEMINI_API_KEY']

FRAMEWORK_NAME = 'kepner_tregoe'

# --- Logging Setup ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if not logging.getLogger().handlers:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(f'FrameworkAgent.{FRAMEWORK_NAME}')

def load_knowledge_base():
    """Loads the knowledge base for the Kepner-Tregoe analysis framework."""
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
You are an expert AI agent specializing in the **Kepner-Tregoe (KT) Method** for systematic problem-solving and decision-making.
Your mission is to guide the user through KT’s four steps and deliver a risk-mitigated decision.
Your complete knowledge base on this framework is provided below, enclosed in <knowledge_base> tags. You must strictly follow the KT process: Situation Appraisal, Problem Analysis, Decision Analysis, and Potential Problem Analysis.

---
<knowledge_base>
{framework_description}
</knowledge_base>
---

**OPERATING INSTRUCTIONS:**

You operate in a two-pass system. Your response format is ALWAYS a single, valid JSON object.

**PASS 1: Information Sufficiency Analysis**
When you receive an `original_query`, your primary task is to determine if you have enough information to begin the KT process. This includes defining the immediate problem or situation, identifying its distinguishing characteristics (Is vs. Is Not), and listing initial options.

- If the information is sufficient, you MUST return the following JSON object:
  `{{"status": "READY", "questions": []}}`

- If the information is insufficient, you MUST generate up to 3 critical questions to clarify the problem scope (Is vs. Is Not), define the objectives and criteria for a successful outcome (Musts/Wants), or identify initial options. Your response MUST be the following JSON object:
  `{{"status": "NEED_INFO", "questions": ["Question about the problem's scope (e.g., what is and is not affected)?", "Question about the key objectives for success?", "..."]}}`

**PASS 2: Final Analysis**
When you receive a `shared_context` that includes `qa_answers`, you MUST perform the final analysis. At this stage, you are PROHIBITED from asking additional questions.

- Use all available information (the original query and all subsequent answers) to systematically execute the four core KT steps: Situation Appraisal, Problem Analysis, Decision Analysis, and Potential Problem Analysis.
- Conclude your analysis with a final, risk-mitigated decision.
- If you determine that critical information is still missing despite the Q&A, you MUST include a `caveat` field in your final report. This caveat should explain the information gap and its potential impact on the analysis.
- Your final output MUST be a JSON object summarizing the outcome of each step:
  `{{"situation_appraisal": "...", "problem_analysis": "...", "decision_analysis": "...", "potential_problem_analysis": "...", "final_risk_mitigated_decision": "...", "caveat": "(Optional) A statement about any remaining information gaps."}}`
"""

def get_agent():
    """
    Builds and returns the Kepner-Tregoe Agent.

    This agent is designed to facilitate rigorous problem-solving and decision-making using the Kepner-Tregoe (KT) Method.
    It operates in two passes:
    1.  **Information Sufficiency Analysis**: Determines if the initial query provides enough information to proceed.
    2.  **Final Analysis**: Conducts the full KT analysis based on the provided context and returns a structured report.
    """
    knowledge = load_knowledge_base()
    final_prompt = PROMPT_TEMPLATE.format(framework_description=knowledge)
    logger.info(f"Rendering prompt for {FRAMEWORK_NAME} (chars={len(final_prompt)})")
    return LlmAgent(
        model="gemini-2.5-pro",
        prompt=final_prompt,
        description="A specialized agent for rigorous, systematic problem-solving and decision-making using the Kepner-Tregoe (KT) Method.",
        tools=[]
    )