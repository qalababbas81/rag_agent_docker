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
    model="llama3.2:1b",
    temperature=0,
    base_url="http://ollama:11434",
    num_predict=100,      # Keeps responses short/fast
    keep_alive="4h",      # 🚀 CRITICAL: Keeps model in memory indefinitely
    num_ctx=2048          # 🚀 Reduces the 'thinking' memory overhead
)
def validation_router(state):

    # if state.get("retry_count", 0) > 2:
    #     return "accept"

    # if state["validation"] == "VALID":
    #     return "accept"

    return "accept"

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
    print ("validate_answer output =>" + result )
    return {"validation":result} 
   

def generate_answer(state: dict):
    last_message = state["messages"][-1]
    question = last_message.content if hasattr(last_message, "content") else str(last_message)
    
    context = state.get("context", None)
  
    tool_output = execute_tool(question, rag_db=lambda q: get_answer(db, q))

    if isinstance(tool_output, dict):
        context = tool_output["context"]
        rows = tool_output.get("rows", None)
        tool_type = tool_output.get("tool_type", "rag")
    else:
            context = tool_output
            rows = None
            tool_type = "rag"
    # 🚀 THE FIX: If SQL, return context immediately. 
    # This stops the 1b model from mangling the characters.
    if "Database Query Result" in context:

        print("DEBUG: SQL bypass triggered.", flush=True)

        response_content = "### 📊 Database Results\n\n" + "\n".join(
            [f"- {' | '.join([str(x) for x in r])}" for r in rows]
        )
        
    else:
        # LLM Path for RAG
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        response = llm.invoke(prompt)
        response_content = response.content

    updated_messages = state["messages"] + [AIMessage(content=response_content)]
    
    return {
        "answer": response_content,
        "context": context,
        "messages": updated_messages,
        "retry_count": state.get("retry_count", 0) + 1
    }

# def generate_answer(state: dict):
#     last_message = state["messages"][-1]
#     question = last_message.content if hasattr(last_message, "content") else str(last_message)
    
#     context = state.get("context", None)
#     if context is None:
#        context = execute_tool(question, rag_db=lambda q: get_answer(db, q))

#     # 🚀 THE FIX: If SQL, return context immediately. 
#     # This stops the 1b model from mangling the characters.
#     if "Database Query Result" in context:
#         print("DEBUG: SQL bypass triggered.", flush=True)
#         response_content = context.replace("Database Query Result:", "### 📊 Database Results\n")
#     else:
#         # LLM Path for RAG
#         prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
#         response = llm.invoke(prompt)
#         response_content = response.content

#     updated_messages = state["messages"] + [AIMessage(content=response_content)]
    
#     return {
#         "answer": response_content,
#         "context": context,
#         "messages": updated_messages,
#         "retry_count": state.get("retry_count", 0) + 1
#     }

def route_after_generate(state: dict):
    context = state.get("context", "")
    
    # 🚀 If context contains SQL results, go straight to the end
    if "Database Query Result" in context:
        return "skip_validation"
    
    # Otherwise, go to the validation node
    return "to_validate"

# Build graph
builder = StateGraph(AgentState)
builder.add_node("generate", generate_answer)
builder.add_node("validate",validate_answer)

builder.set_entry_point("generate")

builder.add_edge("generate", "validate")
#builder.add_edge("generate", END)
builder.add_conditional_edges(
    "generate",
    route_after_generate,
    {
        "skip_validation": END,
        "to_validate": "validate"
    }
)

builder.add_conditional_edges(
    "validate",
    validation_router,
    {
        "accept":END,
        "retry":"generate"
    }
)


graph = builder.compile()
