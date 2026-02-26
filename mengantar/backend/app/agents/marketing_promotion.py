"""
Marketing & Promotion Agent Node.
Handles: Social Proof, Promotion Offers, and Closing.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import get_settings
from app.core.token_counter import log_token_usage
from app.agents.state import ChatState
from app.core.langfuse_handler import get_langfuse_handler

from pathlib import Path

logger = logging.getLogger(__name__)
settings = get_settings()

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

MARKETING_PROMOTION_SYSTEM_PROMPT = load_prompt("marketing_promotion.txt")


async def marketing_promotion_node(state: ChatState) -> ChatState:
    """Marketing promotion agent: handles social proof, promotions, and closing."""
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.7,
        streaming=True,
    )

    last_user_message = ""
    for msg in reversed(state.messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break

    system_prompt = MARKETING_PROMOTION_SYSTEM_PROMPT.format(stage=state.current_stage)
    messages = [SystemMessage(content=system_prompt)] + list(state.messages)

    # Initialize Langfuse handler
    langfuse_handler = get_langfuse_handler(
        session_id=state.thread_id,
        tags=["marketing_promotion", settings.environment]
    )
    callbacks = [langfuse_handler] if langfuse_handler else []

    response = llm.invoke(messages, config={"callbacks": callbacks})
    response_text = response.content

    # Log token usage
    input_text = system_prompt + last_user_message
    token_data = log_token_usage(input_text, response_text, "marketing_promotion", state.thread_id)
    new_token_log = state.token_log + [token_data]

    # Determine next stage
    next_stage = state.current_stage

    # Priority 1: Check for handoff back to customer service
    if "[HANDOFF_TO_CUSTOMER_SERVICE]" in response_text:
        response_text = response_text.replace("[HANDOFF_TO_CUSTOMER_SERVICE]", "").strip()
        next_stage = "consultation"
    # Priority 2: Check for conversation end signals
    elif "[CONVERSATION_END]" in response_text or "[CLOSING_SUCCESS]" in response_text:
        response_text = (
            response_text
            .replace("[CONVERSATION_END]", "")
            .replace("[CLOSING_SUCCESS]", "")
            .strip()
        )
        next_stage = "end"
    # Default: sequential stage progression
    elif state.current_stage == "social_proof":
        next_stage = "promotion"
    elif state.current_stage == "promotion":
        next_stage = "closing"

    return {
        "messages": [AIMessage(content=response_text)],
        "current_stage": next_stage,
        "token_log": new_token_log,
    }
