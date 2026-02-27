from langfuse.langchain import CallbackHandler
from app.core.config import get_settings

settings = get_settings()

def get_langfuse_handler():
    """
    Initialize a Langfuse v3 CallbackHandler.
    Credentials (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL)
    are read automatically from environment variables.
    Returns None if keys are not configured.
    """
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None

    return CallbackHandler()
