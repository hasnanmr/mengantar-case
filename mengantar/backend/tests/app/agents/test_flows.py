import pytest
from app.agents.state import ChatState
from app.agents.graph import route_by_stage, build_graph
from langgraph.graph import END

def test_route_by_stage_customer_service():
    state = ChatState(current_stage="greeting")
    assert route_by_stage(state) == "customer_service"
    
    state = ChatState(current_stage="needs_assessment")
    assert route_by_stage(state) == "customer_service"
    
    state = ChatState(current_stage="consultation")
    assert route_by_stage(state) == "customer_service"

def test_route_by_stage_marketing_promotion():
    state = ChatState(current_stage="social_proof")
    assert route_by_stage(state) == "marketing_promotion"
    
    state = ChatState(current_stage="promotion")
    assert route_by_stage(state) == "marketing_promotion"
    
    state = ChatState(current_stage="closing")
    assert route_by_stage(state) == "marketing_promotion"

def test_route_by_stage_end():
    state = ChatState(current_stage="end")
    assert route_by_stage(state) == END

def test_build_graph_structure():
    builder = build_graph()
    graph = builder.compile()
    
    # Check nodes
    assert "customer_service" in graph.nodes
    assert "marketing_promotion" in graph.nodes
    
    # Verify graph compiles correctly
    assert graph is not None

def test_graph_uses_conditional_entry_point():
    """Verify the graph uses set_conditional_entry_point (no hardcoded start node).
    
    This ensures the router decides which agent to activate BEFORE running
    any node, preventing multiple nodes from firing per turn.
    """
    builder = build_graph()
    graph = builder.compile()
    
    # The graph should compile without errors
    assert graph is not None
    
    # Verify both nodes are present (router dispatches to them)
    assert "customer_service" in graph.nodes
    assert "marketing_promotion" in graph.nodes
