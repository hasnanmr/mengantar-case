"""
Token counting utility using the Qwen tokenizer.
Logs input and output token counts for every LLM exchange.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_tokenizer = None


def get_tokenizer():
    """Lazily load the Qwen tokenizer."""
    global _tokenizer
    if _tokenizer is None:
        try:
            from transformers import AutoTokenizer
            _tokenizer = AutoTokenizer.from_pretrained(
                "Qwen/Qwen2.5-7B-Instruct",  # Use as proxy tokenizer for Qwen3 (same tokenizer family)
                trust_remote_code=True
            )
            logger.info("Qwen tokenizer loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load Qwen tokenizer: {e}. Falling back to character-based estimation.")
    return _tokenizer


def count_tokens(text: str) -> int:
    """Count the number of tokens in a given text string."""
    tokenizer = get_tokenizer()
    if tokenizer:
        return len(tokenizer.encode(text))
    # Fallback: rough estimation (1 token ≈ 4 characters)
    return max(1, len(text) // 4)


def log_token_usage(
    input_text: str,
    output_text: str,
    node_name: str,
    thread_id: Optional[str] = None,
):
    """Log token usage for a given LLM exchange with detailed breakdown."""
    input_tokens = count_tokens(input_text)
    output_tokens = count_tokens(output_text)
    total_tokens = input_tokens + output_tokens

    log_data = {
        "node": node_name,
        "thread_id": thread_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
    logger.info(f"[TOKEN USAGE] {log_data}")
    return log_data
