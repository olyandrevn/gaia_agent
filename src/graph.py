from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import tools_condition

from src.state import AgentState
from src.nodes import assistant, validate_answer, get_tool_node

# Build graph function
def build_graph():
    """Build the graph"""
    builder = StateGraph(AgentState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", get_tool_node)
    builder.add_node("validate_answer", validate_answer)

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
        {
            "tools": "tools",  # Route to tools if needed
            # END: "END"  # Route to end if no tools needed
            END: "validate_answer",  # Route to validate_answer if no tools needed
        },
    )
    builder.add_edge("tools", "assistant")
    # builder.add_edge("assistant", "validate_answer")
    # builder.add_conditional_edges(
    #     "assistant",
    #     ready_to_answer,
    #     {"validate_answer": "validate_answer"},
    # )
    builder.add_edge("validate_answer", END)

    return builder.compile()