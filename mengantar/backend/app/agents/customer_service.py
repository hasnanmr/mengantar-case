"""
Customer Service Agent Node.
Handles: Greeting, Needs Assessment, and Product Consultation.
"""
import logging
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import get_settings
from app.core.token_counter import log_token_usage
from app.rag.knowledge_base import query_knowledge
from app.rag.testimonial_store import testimonial_store
from app.agents.state import ChatState

# Only the introductory sections of the product knowledge are surfaced at product_info stage
PRODUCT_INFO_CONTEXT = """
## Informasi Produk
- **Nama Produk**: Krim Jerawat "Acne Care"
- **Harga**: Rp 75.000
- **Kategori**: Perawatan Kulit / Skincare

## Bahan Aktif (Key Ingredients)
1. **Salicylic Acid (Asam Salisilat)**
   - Bahan eksfoliasi yang membantu membersihkan pori-pori tersumbat.
   - Efektif melawan jerawat dengan menembus lapisan minyak kulit.
   - Membantu mengurangi peradangan dan kemerahan.

2. **Tea Tree Oil (Minyak Pohon Teh)**
   - Antibakteri alami yang sangat efektif melawan bakteri penyebab jerawat.
   - Menenangkan kulit yang merah dan iritasi.
   - Memberikan efek antiseptik tanpa terlalu mengeringkan kulit.
"""

logger = logging.getLogger(__name__)
settings = get_settings()

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

CUSTOMER_SERVICE_SYSTEM_PROMPT = load_prompt("customer_service.txt")


async def customer_service_node(state: ChatState, config: RunnableConfig) -> ChatState:
    """Customer service agent: handles greeting, needs assessment, consultation."""
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.2,
        streaming=True,
        extra_body={"reasoning": {"enabled": False}},
    )

    last_user_message = ""
    for msg in reversed(state.messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break

    # Determine the effective processing stage (treat 'end' as 'greeting' for restarts)
    processing_stage = "greeting" if state.current_stage == "end" else state.current_stage

    # Fetch RAG context or product knowledge depending on stage
    context = ""
    testimonial_info = None
    if processing_stage == "greeting":
        # Deliver the restricted product intro along with the greeting
        context = PRODUCT_INFO_CONTEXT
    elif processing_stage in ("consultation", "needs_assessment"):
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

    # Build a node-specific config: copy incoming (preserving callbacks) and
    # overlay tags + Langfuse metadata so this LLM call is correctly labelled
    # in the Langfuse trace as 'customer_service'.
    node_config: RunnableConfig = {
        **config,
        "tags": list(config.get("tags", [])) + ["customer_service"],
        "metadata": {
            **config.get("metadata", {}),
            "langfuse_session_id": state.thread_id,
            "langfuse_tags": ["customer_service", settings.environment],
        },
    }
    response = llm.invoke(messages, config=node_config)
    response_text = response.content

    # Log token usage
    input_text = system_prompt + last_user_message
    token_data = log_token_usage(input_text, response_text, "customer_service", state.thread_id)
    new_token_log = state.token_log + [token_data]

    # Determine next stage
    next_stage = state.current_stage

    if processing_stage == "greeting":
        # If we just handled a greeting (or a restart from end), transition to needs_assessment
        next_stage = "needs_assessment"

    if "[USER_REFUSED]" in response_text:
        # LLM detected a refusal. We inject the exact closing text here so the prompt doesn't cause hallucination.
        response_text = "Terima kasih sudah menghubungi kami, kami siap untuk membantumu lain kali untuk menangani jerawatmu. Semoga jerawatmu semakin membaik 🌟"
        next_stage = "end"
    elif "[CONVERSATION_END]" in response_text:
        response_text = response_text.replace("[CONVERSATION_END]", "").strip()
        next_stage = "end"
    # Priority 2: Check for explicit marketing handoff signal
    elif "[HANDOFF_TO_MARKETING]" in response_text:
        response_text = response_text.replace("[HANDOFF_TO_MARKETING]", "").strip()
        next_stage = "social_proof"
    elif state.current_stage == "needs_assessment":
        next_stage = "consultation"

    return {
        "messages": [AIMessage(content=response_text)],
        "current_stage": next_stage,
        "user_needs": last_user_message,
        "context": context,
        "token_log": new_token_log,
    }
