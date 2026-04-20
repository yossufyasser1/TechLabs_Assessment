"""Validate that the LangGraph compiles and initializes correctly."""

from src.agent import agent_executor

def test_agent_graph_compiles():
    # If there are syntax errors in the graph edges or nodes, 
    # the agent_executor import and object instantiation will fail.
    assert agent_executor is not None
    assert agent_executor.nodes is not None
