# memory_helper.py
import json
import os
from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama


MEMORY_DIR = "memory"  # ✅ new folder for per-user memory
MAX_MESSAGES = 20
SUMMARY_PROMPT = "Summarize the following conversation in 2-3 concise sentences:"

#llm = ChatOllama(model="llama3.1:latest", temperature=0)
llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0,
    base_url="http://ollama:11434"
)

# Ensure folder exists
os.makedirs(MEMORY_DIR, exist_ok=True)

def get_memory_file(user_id: str) -> str:
    """Return file path for a specific user"""
    return os.path.join(MEMORY_DIR, f"{user_id}.json")

def serialize_message(msg) -> Dict:
    if isinstance(msg, HumanMessage):
        return {"type": "human", "content": msg.content}
    elif isinstance(msg, AIMessage):
        return {"type": "ai", "content": msg.content}
    else:
        return {"type": "unknown", "content": str(msg)}

def deserialize_message(msg_dict) -> object:
    if msg_dict["type"] == "human":
        return HumanMessage(content=msg_dict["content"])
    elif msg_dict["type"] == "ai":
        return AIMessage(content=msg_dict["content"])
    else:
        return msg_dict["content"]

def summarize_messages(messages: List[object]) -> str:
    """Summarize a list of messages using LLM"""
    if not messages:
        return ""
    text = "\n".join([f"{type(m).__name__}: {m.content}" for m in messages])
    prompt = f"{SUMMARY_PROMPT}\n{text}"
    response = llm.invoke(prompt)
    return response.content

def load_memory(user_id: str) -> Dict:
    """Load memory for a specific user"""
    file_path = get_memory_file(user_id)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = [deserialize_message(m) for m in data.get("messages", [])]
        summary = data.get("summary", "")
        return {"messages": messages, "summary": summary}
    except FileNotFoundError:
        return {"messages": [], "summary": ""}

def save_memory(user_id: str, messages: List[object], summary: str = ""):
    """Save memory per user with summarization"""
    if len(messages) > MAX_MESSAGES:
        # summarize older messages
        to_summarize = messages[:-MAX_MESSAGES]
        older_summary = summarize_messages(to_summarize)
        messages = messages[-MAX_MESSAGES:]
        summary = older_summary

    serializable_msgs = [serialize_message(m) for m in messages]
    with open(get_memory_file(user_id), "w", encoding="utf-8") as f:
        json.dump({"messages": serializable_msgs, "summary": summary},
                  f, ensure_ascii=False, indent=2)
        

#----------------------Code before Conversation Summarization Memory----------------------
# MEMORY_DIR = "memory"
# MAX_MESSAGES = 20   # 👈 Memory window size

# # Ensure memory folder exists
# os.makedirs(MEMORY_DIR, exist_ok=True)

# def summarize_messages(messages, llm=None, max_tokens=300):
#     """
#     Summarize conversation to keep memory concise.
#     """
#     if not messages:
#         return ""

#     # Combine conversation into text
#     conversation_text = "\n".join([f"{type(m).__name__}: {m.content}" for m in messages])

#     # If no LLM provided, fallback: first 10 lines
#     if llm is None:
#         return "\n".join(conversation_text.splitlines()[:10])

#     # Call LLM to generate summary
#     prompt = f"Summarize the following conversation concisely:\n{conversation_text}\nSummary:"
#     response = llm.invoke(prompt)
#     return response.content

# def get_memory_file(user_id: str) -> str:
#     """Return file path for specific user"""
#     return os.path.join(MEMORY_DIR, f"{user_id}.json")


# def serialize_message(msg) -> Dict:
#     if isinstance(msg, HumanMessage):
#         return {"type": "human", "content": msg.content}
#     elif isinstance(msg, AIMessage):
#         return {"type": "ai", "content": msg.content}
#     else:
#         return {"type": "unknown", "content": str(msg)}


# def deserialize_message(msg_dict) -> object:
#     if msg_dict["type"] == "human":
#         return HumanMessage(content=msg_dict["content"])
#     elif msg_dict["type"] == "ai":
#         return AIMessage(content=msg_dict["content"])
#     else:
#         return msg_dict["content"]


# def load_memory(user_id: str) -> Dict:
#     """Load memory for a specific user"""
#     file_path = get_memory_file(user_id)

#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         messages = [deserialize_message(m) for m in data.get("messages", [])]
#         return {"messages": messages}
#     except FileNotFoundError:
#         return {"messages": []}


# def save_memory(user_id: str, messages: List[object]):
#     """
#     Trim memory to last MAX_MESSAGES before saving.
#     Save per user.
#     """
#     file_path = get_memory_file(user_id)

#     trimmed_messages = messages[-MAX_MESSAGES:]  # 👈 Rolling window

#     serializable_msgs = [serialize_message(m) for m in trimmed_messages]

#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump({"messages": serializable_msgs}, f, ensure_ascii=False, indent=2)