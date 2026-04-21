"""
LangGraph agent graph definition.

Imports the system prompt and tools, wires the LLM to the tool executor,
and compiles the graph with in-memory checkpointing for multi-turn support.
"""

from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.config import MODEL_NAME, OLLAMA_BASE_URL
from src.tools.registry import AGENT_TOOLS
from src.agent.system_prompt import SYSTEM_PROMPT


# ── LLM setup ────────────────────────────────────────────────
llm = ChatOllama(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    temperature=0.0,  # deterministic — it's managing a database, not writing poetry
)

llm_with_tools = llm.bind_tools(AGENT_TOOLS)


from langchain_core.runnables.config import RunnableConfig

# ── Nodes ─────────────────────────────────────────────────────
def chatbot_node(state: MessagesState, config: RunnableConfig):
    """
    The LLM reasoning node.
    Prepends the system prompt, then calls the LLM with the full conversation.
    The db and user_id are passed in via `config` so tools can access them.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}


tool_node = ToolNode(tools=AGENT_TOOLS)


# ── Graph ─────────────────────────────────────────────────────
workflow = StateGraph(MessagesState)

workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "chatbot")

# If the LLM called a tool → run the tool; otherwise → reply to user and stop
workflow.add_conditional_edges("chatbot", tools_condition)

# After any tool finishes → always go back to the LLM to process the result
workflow.add_edge("tools", "chatbot")


# ── Compile with memory ───────────────────────────────────────
memory = MemorySaver()
agent_executor = workflow.compile(checkpointer=memory)
