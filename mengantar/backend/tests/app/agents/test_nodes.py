import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.state import ChatState
from app.agents.customer_service import customer_service_node
from app.agents.marketing_promotion import marketing_promotion_node

EMPTY_CONFIG = {}

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
         patch("app.agents.marketing_promotion.log_token_usage") as mock_log_mp:
        
        mock_query.return_value = "Mocked RAG context"
        mock_log_cs.return_value = {"tokens": 10}
        mock_log_mp.return_value = {"tokens": 15}
        
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
    
    new_state = await customer_service_node(state, EMPTY_CONFIG)
    
    assert new_state["current_stage"] == "needs_assessment"
    assert len(new_state["messages"]) == 1
    assert isinstance(new_state["messages"][0], AIMessage)
    assert new_state["messages"][0].content == "Hi there! How can I help?"

@pytest.mark.asyncio
async def test_customer_service_node_needs_assessment(mock_llm_response, mock_dependencies):
    """Verify that needs_assessment stage progresses to consultation."""
    state = ChatState(
        messages=[HumanMessage(content="I have dry, oily skin and recurring acne.")],
        current_stage="needs_assessment",
        thread_id="test_thread"
    )
    
    mock_llm_response["cs_response"].content = "Thanks for sharing! Let me look into that for you."
    
    new_state = await customer_service_node(state, EMPTY_CONFIG)
    
    assert new_state["current_stage"] == "consultation"
    assert new_state["messages"][0].content == "Thanks for sharing! Let me look into that for you."

@pytest.mark.asyncio
async def test_customer_service_node_handoff(mock_llm_response, mock_dependencies):
    state = ChatState(
        messages=[HumanMessage(content="Tell me about promotions")],
        current_stage="consultation",
        thread_id="test_thread"
    )
    
    mock_llm_response["cs_response"].content = "Sure! [HANDOFF_TO_MARKETING]"
    
    new_state = await customer_service_node(state, EMPTY_CONFIG)
    
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

    new_state = await marketing_promotion_node(state, EMPTY_CONFIG)

    assert new_state["current_stage"] == "promotion"
    # social_proof stage appends testimonial images as fail-safe
    assert "Check out our reviews!" in new_state["messages"][0].content
    assert "![Testimoni Amanda]" in new_state["messages"][0].content
    assert "![Testimoni Silmi]" in new_state["messages"][0].content

@pytest.mark.asyncio
async def test_marketing_promotion_node_closing(mock_llm_response, mock_dependencies):
    state = ChatState(
        messages=[HumanMessage(content="Okay, I'll buy")],
        current_stage="promotion",
        thread_id="test_thread"
    )

    mock_llm_response["mp_response"].content = "Great! [CLOSING_SUCCESS]"

    new_state = await marketing_promotion_node(state, EMPTY_CONFIG)

    assert new_state["current_stage"] == "end"
    assert new_state["messages"][0].content == "Great!"


# ============================================================================
# Test Handoff Testimoni: Customer Service -> Marketing Promotion
# ============================================================================

@pytest.mark.asyncio
async def test_customer_service_handoff_on_foto_request(mock_llm_response, mock_dependencies):
    """Test: User asks for 'foto testimoni' -> CS should handoff to marketing."""
    state = ChatState(
        messages=[HumanMessage(content="Ada foto testimoni gak?")],
        current_stage="consultation",
        thread_id="test_thread"
    )

    # Simulate CS response with handoff tag
    mock_llm_response["cs_response"].content = "Ada dong! Aku hubungkan kamu ke tim Digital Marketing ya! [HANDOFF_TO_MARKETING]"

    new_state = await customer_service_node(state, EMPTY_CONFIG)

    assert new_state["current_stage"] == "social_proof"
    assert "Ada dong!" in new_state["messages"][0].content
    assert "[HANDOFF_TO_MARKETING]" not in new_state["messages"][0].content


@pytest.mark.asyncio
async def test_customer_service_handoff_on_bukti_request(mock_llm_response, mock_dependencies):
    """Test: User asks for 'bukti nyata' -> CS should handoff to marketing."""
    state = ChatState(
        messages=[HumanMessage(content="Mau liat bukti nyata dong")],
        current_stage="consultation",
        thread_id="test_thread"
    )

    mock_llm_response["cs_response"].content = "Tentu! Aku sambungkan ke tim Digital Marketing yang punya dokumentasi foto testimoni lengkap! [HANDOFF_TO_MARKETING]"

    new_state = await customer_service_node(state, EMPTY_CONFIG)

    assert new_state["current_stage"] == "social_proof"
    assert "[HANDOFF_TO_MARKETING]" not in new_state["messages"][0].content


@pytest.mark.asyncio
async def test_marketing_shows_testimoni_images_after_handoff(mock_llm_response, mock_dependencies):
    """Test: After handoff, marketing (social_proof stage) shows testimoni images."""
    state = ChatState(
        messages=[
            HumanMessage(content="Ada foto testimoni gak?"),
            AIMessage(content="Ada dong! Aku hubungkan kamu ke tim Digital Marketing ya!"),
            HumanMessage(content="Ok, mau liat fotonya")
        ],
        current_stage="social_proof",
        thread_id="test_thread"
    )

    mock_llm_response["mp_response"].content = "Ini nih testimoni dari pengguna ACSBP!"

    new_state = await marketing_promotion_node(state, EMPTY_CONFIG)

    # Marketing should include testimoni images in social_proof stage
    response_content = new_state["messages"][0].content
    assert "Ini nih testimoni" in response_content
    assert "![Testimoni Amanda]" in response_content
    assert "![Testimoni Silmi]" in response_content
    assert new_state["current_stage"] == "promotion"


@pytest.mark.asyncio
async def test_customer_service_product_question_no_handoff(mock_llm_response, mock_dependencies):
    """Test: Regular product question should NOT trigger handoff."""
    state = ChatState(
        messages=[HumanMessage(content="Apa kandungan produk ACSBP?")],
        current_stage="consultation",
        thread_id="test_thread"
    )

    mock_llm_response["cs_response"].content = "ACSBP mengandung BHA, Sulphur, dan Biodegradable Sphere Scrub."

    new_state = await customer_service_node(state, EMPTY_CONFIG)

    # Should stay in consultation, not handoff to marketing
    assert new_state["current_stage"] == "consultation"
    assert "BHA" in new_state["messages"][0].content
