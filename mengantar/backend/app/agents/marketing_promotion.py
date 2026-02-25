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

from pathlib import Path

logger = logging.getLogger(__name__)
settings = get_settings()

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

MARKETING_PROMOTION_SYSTEM_PROMPT = load_prompt("marketing_promotion.txt")


def marketing_promotion_node(state: ChatState) -> ChatState:
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
    response = llm.invoke(messages)
    response_text = response.content

    # Log token usage
    input_text = system_prompt + last_user_message
    token_data = log_token_usage(input_text, response_text, "marketing_promotion", state.thread_id)
    new_token_log = state.token_log + [token_data]

    # Determine next stage
    next_stage = state.current_stage
    if state.current_stage == "social_proof":
        next_stage = "promotion"
    elif state.current_stage == "promotion":
        next_stage = "closing"

    if "[CONVERSATION_END]" in response_text or "[CLOSING_SUCCESS]" in response_text:
        response_text = (
            response_text
            .replace("[CONVERSATION_END]", "")
            .replace("[CLOSING_SUCCESS]", "")
            .strip()
        )
        next_stage = "end"

    return ChatState(
        messages=state.messages + [AIMessage(content=response_text)],
        current_stage=next_stage,
        thread_id=state.thread_id,
        user_needs=state.user_needs,
        context=state.context,
        token_log=new_token_log,
    )
