
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from prompts import get_system_instructions
import os
from state import State
from dotenv import load_dotenv
from pathlib import Path

# LOAD SECRETS 
current_file_path = Path(__file__).resolve()
secrets_path = current_file_path.parent.parent / ".secrets"
load_dotenv(dotenv_path=secrets_path)

# IMPORT ALL 3 TOOLS
from tools import dubai_budget_tool, search_dubai_infrastructure, get_live_exchange_rate

# Define the LLM
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "openai:gpt-4o-mini",
    temperature=0.7,
    base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
    api_key='any value',
    default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
)

# BIND ALL 3 TOOLS (Requirement: 3 Services)
tools = [dubai_budget_tool, search_dubai_infrastructure, get_live_exchange_rate]
llm_with_tools = llm.bind_tools(tools)

# The Guardrail Node
def guardrail_node(state: State):
    last_message = state["messages"][-1].content.lower()
    
    # Check for the forbidden topics from your prompt
    forbidden = ['taylor swift', 'cats', 'dogs', 'horoscopes', 'zodiac']
    
    if any(topic in last_message for topic in forbidden):
        return {
            "is_safe": False, 
            "messages": [AIMessage(content="I am a specialized AI Infrastructure Consultant. I cannot discuss pop culture, pets, or astrology.")]
        }

    return {"is_safe": True}

# The Model Node (The Brain)
def assistant_node(state: State):
    instructions = get_system_instructions()
    messages = [SystemMessage(content=instructions)] + state["messages"]
    
    # Use llm_with_tools so it can actually call the search/calc/api
    response = llm_with_tools.invoke(messages)
    
    # Increment the llm_calls counter from state.py
    current_calls = state.get("llm_calls", 0)
    
    return {
        "messages": [response],
        "llm_calls": current_calls + 1
    }

# The Router
def should_continue(state: State):
    # If the guardrail marked it unsafe, we go to END immediately
    if state.get("is_safe") is False:
        return "end"
    # Otherwise, proceed to the assistant
    return "assistant"
    

