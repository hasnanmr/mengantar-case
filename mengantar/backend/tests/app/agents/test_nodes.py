import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.state import ChatState
from app.agents.customer_service import customer_service_node
from app.agents.marketing_promotion import marketing_promotion_node

@pytest.fixture
def mock_llm_response():
    with patch("app.agents.customer_service.ChatOpenAI") as mock_llm_cs, \
         patch("app.agents.marketing_promotion.ChatOpenAI") as mock_llm_mp:
        
        # Mock for Customer Service
        mock_instance_cs = mock_llm_cs.return_value
        mock_response_cs = MagicMock()
        mock_response_cs.content = "CS Response [HANDOFF_TO_MARKETING]"
        mock_instance_cs.invoke.return_value = mock_response_cs
        
        # Mock for Marketing Promotion
        mock_instance_mp = mock_llm_mp.return_value
        mock_response_mp = MagicMock()
        mock_response_mp.content = "MP Response [CONVERSATION_END]"
        mock_instance_mp.invoke.return_value = mock_response_mp
        
        yield {
            "cs_instance": mock_instance_cs,
            "mp_instance": mock_instance_mp,
            "cs_response": mock_response_cs,
            "mp_response": mock_response_mp
        }

@pytest.fixture
def mock_dependencies():
    with patch("app.agents.customer_service.query_knowledge") as mock_query, \
         patch("app.agents.customer_service.log_token_usage") as mock_log_cs, \
         patch("app.agents.marketing_promotion.log_token_usage") as mock_log_mp, \
         patch("app.agents.customer_service.get_langfuse_handler") as mock_lf_cs, \
         patch("app.agents.marketing_promotion.get_langfuse_handler") as mock_lf_mp:
        
        mock_query.return_value = "Mocked RAG context"
        mock_log_cs.return_value = {"tokens": 10}
        mock_log_mp.return_value = {"tokens": 15}
        mock_lf_cs.return_value = None
        mock_lf_mp.return_value = None
        
        yield {
            "query": mock_query,
            "log_cs": mock_log_cs,
            "log_mp": mock_log_mp
        }

@pytest.mark.asyncio
async def test_customer_service_node_greeting(mock_llm_response, mock_dependencies):
    state = ChatState(
        messages=[HumanMessage(content="Hello")],
        current_stage="greeting",
        thread_id="test_thread"
    )
    
    mock_llm_response["cs_response"].content = "Hi there! How can I help?"
    
    new_state = await customer_service_node(state)
    
    assert new_state["current_stage"] == "needs_assessment"
    assert len(new_state["messages"]) == 1
    assert isinstance(new_state["messages"][0], AIMessage)
    assert new_state["messages"][0].content == "Hi there! How can I help?"

@pytest.mark.asyncio
async def test_customer_service_node_handoff(mock_llm_response, mock_dependencies):
    state = ChatState(
        messages=[HumanMessage(content="Tell me about promotions")],
        current_stage="consultation",
        thread_id="test_thread"
    )
    
    mock_llm_response["cs_response"].content = "Sure! [HANDOFF_TO_MARKETING]"
    
    new_state = await customer_service_node(state)
    
    assert new_state["current_stage"] == "social_proof"
    assert new_state["messages"][0].content == "Sure!"

@pytest.mark.asyncio
async def test_marketing_promotion_node_progression(mock_llm_response, mock_dependencies):
    state = ChatState(
        messages=[HumanMessage(content="I'm interested")],
        current_stage="social_proof",
        thread_id="test_thread"
    )
    
    mock_llm_response["mp_response"].content = "Check out our reviews!"
    
    new_state = await marketing_promotion_node(state)
    
    assert new_state["current_stage"] == "promotion"
    assert new_state["messages"][0].content == "Check out our reviews!"

@pytest.mark.asyncio
async def test_marketing_promotion_node_closing(mock_llm_response, mock_dependencies):
    state = ChatState(
        messages=[HumanMessage(content="Okay, I'll buy")],
        current_stage="promotion",
        thread_id="test_thread"
    )
    
    mock_llm_response["mp_response"].content = "Great! [CLOSING_SUCCESS]"
    
    new_state = await marketing_promotion_node(state)
    
    assert new_state["current_stage"] == "end"
    assert new_state["messages"][0].content == "Great!"
