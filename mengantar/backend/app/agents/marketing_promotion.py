"""
Marketing & Promotion Agent Node.
Handles: Social Proof, Promotion Offers, and Closing.
"""
import base64
import logging
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import get_settings
from app.core.token_counter import log_token_usage
from app.agents.state import ChatState

from pathlib import Path

logger = logging.getLogger(__name__)
settings = get_settings()

PROMPTS_DIR = Path(__file__).parent / "prompts"
STATIC_DIR = Path(__file__).parent.parent.parent / "static"

# Testimonial images with their web-accessible markdown references
TESTIMONIAL_IMAGES = [
    {
        "path": STATIC_DIR / "testimonials" / "amanda.jpg",
        "markdown_ref": "![Testimoni Amanda](/static/testimonials/amanda.jpg)",
        "name": "Amanda",
    },
    {
        "path": STATIC_DIR / "testimonials" / "silmi.jpg",
        "markdown_ref": "![Testimoni Silmi](/static/testimonials/silmi.jpg)",
        "name": "Silmi",
    },
]


async def _encode_testimonial_images() -> list[dict]:
    """Encode testimonial images as base64 for multimodal LLM input."""
    from app.rag.testimonial_store import testimonial_store
    
    image_contents = []
    for info in TESTIMONIAL_IMAGES:
        name = info["name"]
        
        # 1. DB First
        db_record = await testimonial_store.search_testimonial(name, threshold=0.8)
        
        if db_record and db_record.get("image_path"):
            img_path = STATIC_DIR / db_record["image_path"].replace("static/", "")
            logger.info(f"Using DB testimonial for {name} from {img_path}")
        else:
            # 2. Fallback to hardcoded prompt references
            img_path = info["path"]
            logger.info(f"Using fallback testimonial for {name} from {img_path}")
            
        if not img_path.exists():
            logger.warning(f"Testimonial image not found: {img_path}")
            continue
            
        with open(img_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        ext = img_path.suffix.lstrip(".").lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        image_contents.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64_data}"},
        })
        logger.info(f"Injected vision context for {name}'s testimonial image")
        
    return image_contents

async def _build_multimodal_messages(messages: list, user_text: str) -> list:
    """Replace the last HumanMessage with a multimodal one containing testimonial images."""
    image_contents = await _encode_testimonial_images()
    if not image_contents:
        return messages  # Fallback: no images available, use plain messages

    # Build multimodal content: images first, then user text
    multimodal_content = image_contents + [{"type": "text", "text": user_text}]

    # Walk messages in reverse and replace only the last HumanMessage
    result = list(messages)
    for i in range(len(result) - 1, -1, -1):
        if isinstance(result[i], HumanMessage):
            result[i] = HumanMessage(content=multimodal_content)
            break
    return result


def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


MARKETING_PROMOTION_SYSTEM_PROMPT = load_prompt("marketing_promotion.txt")


async def marketing_promotion_node(state: ChatState, config: RunnableConfig) -> ChatState:
    """Marketing promotion agent: handles social proof, promotions, and closing."""
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

    system_prompt = MARKETING_PROMOTION_SYSTEM_PROMPT.format(stage=state.current_stage)

    base_messages = [SystemMessage(content=system_prompt)] + list(state.messages)

    # Inject vision context (actual testimonial images) during social_proof stage
    if state.current_stage == "social_proof":
        logger.info("social_proof stage: injecting testimonial images as vision context")
        messages_to_send = await _build_multimodal_messages(base_messages, last_user_message)
    else:
        messages_to_send = base_messages

    # Build a node-specific config: copy incoming (preserving callbacks) and
    # overlay tags + Langfuse metadata so this LLM call is correctly labelled
    # in the Langfuse trace as 'marketing_promotion'.
    node_config: RunnableConfig = {
        **config,
        "tags": list(config.get("tags", [])) + ["marketing_promotion"],
        "metadata": {
            **config.get("metadata", {}),
            "langfuse_session_id": state.thread_id,
            "langfuse_tags": ["marketing_promotion", settings.environment],
        },
    }
    response = llm.invoke(messages_to_send, config=node_config)
    response_text = response.content

    # Fail-safe: Ensure image markdown is present if we are in social_proof stage
    if state.current_stage == "social_proof":
        # Check if the LLM actually output the markdown tags
        if "![Testimoni Amanda]" not in response_text and "![Amanda]" not in response_text:
            response_text += "\n\n![Testimoni Amanda](/static/testimonials/amanda.jpg)"
        if "![Testimoni Silmi]" not in response_text and "![Silmi]" not in response_text:
            response_text += "\n\n![Testimoni Silmi](/static/testimonials/silmi.jpg)"

    # Log token usage
    input_text = system_prompt + last_user_message
    token_data = log_token_usage(input_text, response_text, "marketing_promotion", state.thread_id)
    new_token_log = state.token_log + [token_data]

    # Determine next stage
    next_stage = state.current_stage
    if next_stage == "end":
        next_stage = "social_proof"

    # Identify next stage or stream ending commands
    if "[USER_REFUSED]" in response_text:
        # LLM detected a refusal. Inject the exact string here.
        response_text = "Terima kasih sudah menghubungi kami, kami siap untuk membantumu lain kali dalam menangani jerawatmu. Semoga jerawatmu semakin membaik 🌟"
        next_stage = "end"
    # Priority 1: Check for handoff back to customer service
    elif "[HANDOFF_TO_CUSTOMER_SERVICE]" in response_text:
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
