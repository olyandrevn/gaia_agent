from langchain_ollama import ChatOllama
from langchain_together import ChatTogether

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from src.state import AgentState
from src.tools import (
    calculator,
    wiki_search,
    web_search,
    reverse_string,
    tool_download_image,
    tool_read_files,
)

class AnswerTemplate(BaseModel):
    final_answer: str = Field(description="Final answer to the question")


tools = [
    calculator,
    wiki_search,
    # web_search,
    reverse_string,
    # tool_download_image,
    tool_read_files,
]

def get_tool_node(state: AgentState):
    return ToolNode(tools)

# Assistant node - generates responses
def assistant(state: AgentState):
    """Generate a response using the LLM."""
    '''
    llama fast but dont use tools
        meta-llama/Llama-3.3-70B-Instruct-Turbo
        meta-llama/Llama-3-70B-Instruct-Turbo
        meta-llama/Meta-Llama-3-70B-Instruct-Turbo
        meta-llama/Llama-3-70b-chat-hf
        Qwen/Qwen2.5-72B-Instruct-Turbo
        Qwen/Qwen3-235B-A22B-Instruct-2507-tput
    '''

    # llm = ChatOllama(
    #     # model="llama3.2",
    #     model="qwen3",
    #     # model="qwen3:4b",
    #     temperature=0,
    #     num_ctx=16384,
    # )

    llm = ChatTogether(
        model="Qwen/QwQ-32B",
        max_tokens=None,
        temperature=0,
        timeout=None,
        max_retries=2,
        top_p=0.8,
        # truncation='auto',
    )   

    # llm = ChatTogether(
    #     model="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    #     max_tokens=None,
    #     temperature=0,
    #     timeout=None,
    #     max_retries=4,
    # )  

    messages = []
    init = False
    if len(state["messages"]) == 0:
        if len(state["file_name"]) == 0:
            human_message = f'{state["question"]}'
        else:
            human_message = f'{state["question"]} File: {state["file_name"]}'
        messages = [
            SystemMessage(content=state["system_message"]),
            HumanMessage(content=human_message),
        ]
        init = True
        for m in messages:
            m.pretty_print()

    # Bind tools to the LLM
    chat_with_tools = llm.bind_tools(tools)
    response = chat_with_tools.invoke(messages if init else state["messages"])
    messages.append(response)
    # print(response)
    messages[-1].pretty_print()
    # print(f"Assistant response: {response.content[:50]}...")
    return {
        "messages": messages,
        "last_ai_message": response.content,  # if state["messages"] and isinstance(state["messages"][-1], AIMessage) else None
    }


# def validate_answer(state: AgentState):
#     """Validate the final answer."""
#     llm = ChatOllama(
#         model="llama3.2",
#         # model="qwen3",
#         # model="qwen3:4b",
#         temperature=0,
#     )

#     def escape_braces(text):
#         return text.replace("{", "{{").replace("}", "}}")

#     query = "---\n\nYou are given a conversation between a human and an AI agent. Identify the final answer provided by the agent. Then, format that final answer according to the formatting rules described in the system message, but do not alter the content of the answer itself. Only apply formatting as instructed. Answer in JSON format."

#     # Set up a parser + inject instructions into the prompt template.
#     '''
#         Создаётся парсер, который преобразует ответ модели в JSON-структуру, соответствующую AnswerTemplate (предположительно, это Pydantic-модель с полем final_answer).
#         https://python.langchain.com/docs/how_to/output_parser_json/
#     '''
#     parser = JsonOutputParser(pydantic_object=AnswerTemplate)
#     prompt = PromptTemplate(
#         template=(
#             f"SYSTEM MESSAGE: {state['system_message']}\n\n"
#             f"HUMAN QUERY: {escape_braces(state['question'])}\n\n"
#             f"AGENT ANSWER: {escape_braces(state['last_ai_message'])}\n\n"
#             f"{query}\n\n"
#             "{format_instructions}"
#         ),
#         input_variables=["query"],
#         partial_variables={"format_instructions": parser.get_format_instructions()},
#     )
#     # print(prompt)
#     chain = prompt | llm | parser
#     # final_answer = chain.invoke(
#     #     {"format_instructions": parser.get_format_instructions()}
#     # )
#     final_answer = chain.invoke({"query": query})
#     print(final_answer)
#     final_answer = final_answer["final_answer"]
#     # logger.info(f"Final answer: {final_answer}")
#     return {"final_answer": final_answer}

def validate_answer(state: AgentState):
    """Validate the final answer."""
  
    pattern = 'FINAL ANSWER: '

    i = state['last_ai_message'].find(pattern)
    final_answer = state['last_ai_message'][i + len(pattern):]
    print(final_answer)
    return {"final_answer": final_answer}

def ready_to_answer(state: AgentState):
    if state["ready_to_answer"]:
        return "validate_answer"
    else:
        return "assistant"