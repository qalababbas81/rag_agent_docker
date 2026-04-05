from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from graph import graph
from memory_helper import load_memory, save_memory

app = FastAPI()


@app.post("/ask-stream")
async def ask_stream(data: dict):

    """
    Payload:
    {
        "user_id": "john",
        "question": "What is leave policy?"
    }
    """

    async def generator():
        try:

            user_id = data.get("user_id")
            question = data.get("question")

            if not user_id or not question:
                yield "user_id and question are required"
                return

            # 🔹 Load memory
            previous_state = load_memory(user_id)

            user_message = HumanMessage(content=question)

            state = {
                "messages": previous_state["messages"] + [user_message],
                "summary": previous_state.get("summary", "")
            }

            # 🔹 Run LangGraph
            result = graph.invoke(state)

            answer = result["answer"]

            # 🔹 Save updated memory
            save_memory(user_id, result["messages"], summary=state.get("summary", ""))

            # 🔹 Stream response word by word
            for word in answer.split():
                yield word + " "

        except Exception as e:
            yield str(e)

    return StreamingResponse(generator(), media_type="text/plain")
#--------------------------------------Code Before Sreaming -----------------------------
# app = FastAPI()

# @app.post("/ask")
# def ask(data: dict):
#     """
#     Payload:
#     {
#         "user_id": "john",
#         "question": "What is leave policy?"
#     }
#     """
#     try:
#         user_id = data.get("user_id")
#         question = data.get("question")

#         if not user_id or not question:
#             return {"error": "user_id and question are required"}

#         # 🔥 Load memory dynamically for this user
#         previous_state = load_memory(user_id)

#         # Wrap user question
#         user_message = HumanMessage(content=question)

#         state = {
#             "messages": previous_state["messages"] + [user_message],
#             "summary": previous_state.get("summary", "")  # 🔥 include summary
#         }

#         # Call graph
#         result = graph.invoke(state)
#         response = result["answer"]

#         # 🔥 Save memory for this user including summary
#         save_memory(user_id, result["messages"], summary=state.get("summary", ""))

#         return {"answer": response}

#     except Exception as e:
#         return {"error": str(e)}

#------------------------------Code before multi-user summarization memory
# app = FastAPI()

# @app.post("/ask")
# def ask(data: dict):
#     """
#     Payload:
#     {
#         "user_id": "john",
#         "question": "What is leave policy?"
#     }
#     """
#     try:
#         user_id = data.get("user_id")
#         question = data.get("question")

#         if not user_id or not question:
#             return {"error": "user_id and question are required"}

#         # 🔥 Load memory dynamically for this user
#         previous_state = load_memory(user_id)

#         # Wrap user question
#         user_message = HumanMessage(content=question)

#         state = {
#             "messages": previous_state["messages"] + [user_message]
#         }

#         # Call graph
#         result = graph.invoke(state)
#         response = result["answer"]

#         # 🔥 Save memory for this user
#         save_memory(user_id, result["messages"])

#         return {"answer": response}

#     except Exception as e:
#         return {"error": str(e)}