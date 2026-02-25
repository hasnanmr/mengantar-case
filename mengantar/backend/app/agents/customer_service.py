"""
Customer Service Agent Node.
Handles: Greeting, Needs Assessment, and Product Consultation.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import get_settings
from app.core.token_counter import log_token_usage
from app.rag.knowledge_base import query_knowledge
from app.agents.state import ChatState

from pathlib import Path

logger = logging.getLogger(__name__)
settings = get_settings()

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

CUSTOMER_SERVICE_SYSTEM_PROMPT = load_prompt("customer_service.txt")


def customer_service_node(state: ChatState) -> ChatState:
    """Customer service agent: handles greeting, needs assessment, consultation."""
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.7,
        streaming=False,
    )

    last_user_message = ""
    for msg in reversed(state.messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break

    # Fetch RAG context for consultation
    context = ""
    if state.current_stage in ("consultation", "needs_assessment"):
        context = query_knowledge(last_user_message)

    system_prompt = CUSTOMER_SERVICE_SYSTEM_PROMPT.format(
        context=context or "Gunakan pengetahuan umum tentang produk Acne Care.",
        stage=state.current_stage,
    )

    messages = [SystemMessage(content=system_prompt)] + list(state.messages)
    response = llm.invoke(messages)
    response_text = response.content

    # Log token usage
    input_text = system_prompt + last_user_message
    token_data = log_token_usage(input_text, response_text, "customer_service", state.thread_id)
    new_token_log = state.token_log + [token_data]

    # Determine next stage
    next_stage = state.current_stage
    if state.current_stage == "greeting":
        next_stage = "needs_assessment"
    elif state.current_stage == "needs_assessment":
        next_stage = "consultation"
    elif "[HANDOFF_TO_MARKETING]" in response_text:
        response_text = response_text.replace("[HANDOFF_TO_MARKETING]", "").strip()
        next_stage = "social_proof"

    return ChatState(
        messages=state.messages + [AIMessage(content=response_text)],
        current_stage=next_stage,
        thread_id=state.thread_id,
        user_needs=last_user_message,
        context=context,
        token_log=new_token_log,
    )
