from typing import Optional
from langgraph.graph import MessagesState

# Define the state type with annotations
class AgentState(MessagesState):
    system_message: str
    last_ai_message: str
    question: str
    file_name: str
    final_answer: str
    ready_to_answer: bool
    error: Optional[str]