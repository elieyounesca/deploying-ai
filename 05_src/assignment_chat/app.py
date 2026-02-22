print("--- DEBUG: Starting App.py now... ---")


import gradio as gr
from main import app  # Imports your compiled LangGraph workflow
from langchain_core.messages import HumanMessage
import uuid

# --- DEBUG: Starting App.py now... ---
print("🚀 Starting Dubai AI Strategist UI...")

def dubai_chat_wrapper(message, history):
    """
    Bridge between Gradio UI and LangGraph logic.
    """
    try:
        # 1. Prepare the input for LangGraph
        # We wrap the string message in a HumanMessage to avoid 'tuple' errors in nodes.py
        inputs = {"messages": [HumanMessage(content=str(message))]}
        
        # 2. Configuration for Memory (Thread ID)
        # Using a fixed ID for the assignment, but could be unique per session
        config = {"configurable": {"thread_id": "dubai_assignment_session"}}
        
        # 3. Invoke the Graph
        result = app.invoke(inputs, config=config)
        
        # 4. Extract the final response text
        # LangGraph returns the full history; we only want the last AI response
        final_answer = result["messages"][-1].content
        
        return final_answer

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- UI Layout ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🇦🇪 Dubai AI Project Strategist
    ### Specialized Consultant for AI Infrastructure & Budgeting
    *Ask me about the Dubai AI Report, USD to AED conversions, or token costs.*
    """)
    
    chat_interface = gr.ChatInterface(
        fn=dubai_chat_wrapper,
        examples=[
            "What are the goals of the Dubai AI blueprint?",
            "Convert $500 to AED.",
            "Calculate the cost for 5 million tokens with a $1000 budget."
        ],
        cache_examples=False,
    )

# --- Launch ---
if __name__ == "__main__":
    # The app will run on http://127.0.0.1:7860
    demo.launch(server_name="127.0.0.1", server_port=7860)