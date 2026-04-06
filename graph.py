import os
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from state import AgentState
from loader_multi import load_all_docs
from splitter import split_docs
from tools.tool_router import execute_tool
from vectorstore import create_vectorestore
from retriever import get_answer
import pyodbc
from tools.sql_tool import run_sql_query

# Load documents and build RAG
docs = load_all_docs("docs")
#print(len(docs))
#print(pyodbc.drivers())
#for d in docs:
 #   print(d.metadata)
chunks = split_docs(docs)
db = create_vectorestore(chunks)

#llm = ChatOllama(model="llama3.1:latest", temperature=0)
llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0,
    base_url="http://ollama:11434",
    num_predict=100
)
def validation_router(state):

    if state.get("retry_count", 0) > 2:
        return "accept"

    if state["validation"] == "VALID":
        return "accept"

    return "retry"

def validate_answer(state:dict):

      # Get context from state FIRST
    context = state.get("context", "")

    # Skip validation for SQL results
    if "Database Query Result" in context:
        return {"validation": "VALID"}
    
    question = state["messages"][-2].content
    answer = state["answer"]
    context = state["context"]

    prompt = f"""
    You are a strict validator.

    Check if the answer is supported by the context.

    Context:
    {context}

    Question:
    {question}

    Answer:
    {answer}

    Respond with ONLY one word:

    VALID
    or
    INVALID
    """
    result = llm.invoke(prompt).content.strip()
    return {"validation":result}


def generate_answer(state: dict):
    """
    state = {
        "messages": [...],  # list of HumanMessage/AIMessage for this user
        "summary": "..."    # optional summary of older messages
    }
    """

    last_message = state["messages"][-1]
    question = last_message.content if hasattr(last_message, "content") else str(last_message)
    
      # 🔹 Run tool ONLY once
    context = state.get("context", None)

# Run tool only if context not already present
    if context is None:
       context = execute_tool(question, rag_db=lambda q: get_answer(db, q))

    # 🔹 Include previous messages (excluding last question) and summary
    memory_messages = state.get("messages", [])[:-1]
    memory_summary = state.get("summary", "")

    memory_text = "\n".join([f"{type(m).__name__}: {m.content}" for m in memory_messages])

    # 🔹 Build LLM prompt with summary + recent messages
    prompt = f"""
You are an intelligent assistant.

Answer the user question using the provided context.

The context may come from:
1. Company documents
2. SQL database results

Rules:
- Use ONLY the provided context.
- If context contains SQL results, interpret them correctly.
- If the answer is not present, say:
"Information not available in provided data."
- Do not invent information.

Context:
{context}

User Question:
{question}

Answer clearly.
"""

    response = llm.invoke(prompt)

    updated_messages = state["messages"] + [AIMessage(content=response.content)]

    retry_count = state.get("retry_count", 0)
    return {
        "answer": response.content,
        "context":context,
        "messages": updated_messages,
        "retry_count": retry_count + 1
    }


# Build graph
builder = StateGraph(AgentState)
builder.add_node("generate", generate_answer)
builder.add_node("validate",validate_answer)

builder.set_entry_point("generate")

builder.add_edge("generate", "validate")
builder.add_conditional_edges(
    "validate",
    validation_router,
    {
        "accept":END,
        "retry":"generate"
    }
)

graph = builder.compile()
