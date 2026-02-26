from langfuse.langchain import CallbackHandler
from app.core.config import get_settings

settings = get_settings()

def get_langfuse_handler(session_id: str = None, trace_id: str = None, tags: list[str] = None):
    """
    Initialize Langfuse CallbackHandler with credentials and context.
    
    Args:
        session_id: The conversation thread ID for session tracking.
        trace_id: Optional specific trace ID.
        tags: Optional list of tags for the trace.
    """
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None
        
    return CallbackHandler()
