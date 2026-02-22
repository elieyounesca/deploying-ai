import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition 

from state import State
from nodes import guardrail_node, assistant_node, should_continue
# IMPORTANT: Import all 3 tools to register them in the Graph
from tools import dubai_budget_tool, search_dubai_infrastructure, get_live_exchange_rate

load_dotenv(".env")
load_dotenv(".secrets")

workflow = StateGraph(State)

# 1. Add Nodes
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("assistant", assistant_node)

# REQUIREMENT: ToolNode must contain all 3 services
workflow.add_node("tools", ToolNode([
    dubai_budget_tool, 
    search_dubai_infrastructure, 
    get_live_exchange_rate
])) 

# 2. Wiring (Edges)

# Start -> Guardrail
workflow.add_edge(START, "guardrail")

# Guardrail -> Assistant OR End (Using your custom router)
workflow.add_conditional_edges(
    "guardrail",
    should_continue, # This function checks state["is_safe"]
    {
        "assistant": "assistant",
        "end": END
    }
)

# Assistant -> Tools OR End (Using built-in logic for tool calls)
workflow.add_conditional_edges(
    "assistant",
    tools_condition, # Built-in: checks if LLM created tool_calls
)

# Tools -> Assistant (Loop back to explain the data found)
workflow.add_edge("tools", "assistant")

# 3. Compilation
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 4. Test Run
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "dubai_user_001"}}
    user_input = {"messages": [("user", "What does the Dubai AI Blueprint say about data centers?")]}

    for event in app.stream(user_input, config=config):
        print(event)





























