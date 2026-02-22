from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
import operator

class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    
    # This is custom flag for the Guardrail
    is_safe: bool
    llm_calls: int