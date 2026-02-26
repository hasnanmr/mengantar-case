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
from app.rag.testimonial_store import testimonial_store
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

CUSTOMER_SERVICE_SYSTEM_PROMPT = load_prompt("customer_service.txt")


async def customer_service_node(state: ChatState) -> ChatState:
    """Customer service agent: handles greeting, needs assessment, consultation."""
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

    # Fetch RAG context for consultation
    context = ""
    testimonial_info = None
    if state.current_stage in ("consultation", "needs_assessment"):
        context = query_knowledge(last_user_message)
        
        # Check for image intent
        image_keywords = ["foto", "gambar", "testimoni", "bukti", "liat", "lihat"]
        if any(kw in last_user_message.lower() for kw in image_keywords):
            testimonial_info = await testimonial_store.search_testimonial(last_user_message)

    # If testimonial found, add to context
    if testimonial_info:
        image_url = f"/static/{testimonial_info['image_path']}"
        context += f"\n\n[TESTIMONIAL_IMAGE] Ada foto testimoni relevan: {image_url}. " \
                   f"Deskripsi foto: {testimonial_info['description']}. " \
                   f"Pastikan untuk memberitahu user bahwa ada foto yang bisa dilihat."

    system_prompt = CUSTOMER_SERVICE_SYSTEM_PROMPT.format(
        context=context or "Gunakan pengetahuan umum tentang produk Acne Care.",
        stage=state.current_stage,
    )

    messages = [SystemMessage(content=system_prompt)] + list(state.messages)
    
    # Initialize Langfuse handler
    langfuse_handler = get_langfuse_handler(
        session_id=state.thread_id,
        tags=["customer_service", settings.environment]
    )
    callbacks = [langfuse_handler] if langfuse_handler else []

    response = llm.invoke(messages, config={"callbacks": callbacks})
    response_text = response.content

    # Log token usage
    input_text = system_prompt + last_user_message
    token_data = log_token_usage(input_text, response_text, "customer_service", state.thread_id)
    new_token_log = state.token_log + [token_data]

    # Determine next stage
    # Priority 1: Check for explicit marketing handoff signal at ANY stage
    next_stage = state.current_stage
    if "[HANDOFF_TO_MARKETING]" in response_text:
        response_text = response_text.replace("[HANDOFF_TO_MARKETING]", "").strip()
        next_stage = "social_proof"
    elif state.current_stage == "greeting":
        next_stage = "needs_assessment"
    elif state.current_stage == "needs_assessment":
        next_stage = "consultation"

    return {
        "messages": [AIMessage(content=response_text)],
        "current_stage": next_stage,
        "user_needs": last_user_message,
        "context": context,
        "token_log": new_token_log,
    }
