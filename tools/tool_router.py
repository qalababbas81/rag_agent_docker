from langchain_ollama import ChatOllama
from tools.sql_tool import run_sql_query


# def route_tool (tool_name, input_data):
#     if tool_name == "sql_query":
#         return run_sql_query(input_data)
#     else:
#         return {"error":"Tool not found"}
    
#llm = ChatOllama(model="llama3.1:latest", temperature=0)
llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0,
    base_url="http://ollama:11434",
    num_predict=100,      # Keeps responses short/fast
    keep_alive="4h",      # 🚀 CRITICAL: Keeps model in memory indefinitely
    num_ctx=2048          # 🚀 Reduces the 'thinking' memory overhead
)
SQL_KEYWORDS = [
    "employee", "salary", "revenue", "id", "email", "address", "top", "count", "list"
]

def decide_tool_and_query(question: str) -> dict:
    """
    Decide whether to use SQL or RAG.
    If SQL, convert natural language to SQL safely.
    Returns:
        {
            "tool": "sql" or "rag",
            "sql_query": "..." or None
        }
    """
    # Quick keyword detection
    words = question.lower().split()

    if any(word in words for word in SQL_KEYWORDS):
        # Ask LLM to convert NL question → SQL safely
        prompt = f"""
You are a Microsoft SQL Server expert.
Convert this natural language request into a T-SQL query.
In  query select include only Name , Email and Address.
Database table: Employees(Id, Name, Email, Address, EmpImagePath).

IMPORTANT: 
- Use 'SELECT TOP N' for limiting results. 
- DO NOT use 'LIMIT'.
- Only return the SQL code.

Request: "{question}"
"""
        response = llm.invoke(prompt)
        sql_query = response.content.strip()

        # Remove markdown formatting
        sql_query = sql_query.replace("```sql", "")
        sql_query = sql_query.replace("```", "")
        sql_query = sql_query.replace("`", "")

        sql_query = sql_query.strip()
        
        return {"tool": "sql", "sql_query": sql_query}
    else:
        return {"tool": "rag", "sql_query": None}
    
def execute_tool(question: str, rag_db=None):
    """
    Decides tool, executes it, and returns context for LLM.
    """

    decision = decide_tool_and_query(question)
    context=""
    print("TOOL SELECTED:", decision["tool"])
    print("QUESTION:", question)

    if decision["tool"] == "sql":
        try:
            print("Inside SQL Tool")
            result = run_sql_query(decision["sql_query"])

            print("RAW SQL RESULT TYPE:", type(result))
            print("RAW SQL RESULT:", result)
            
            formatted_rows = []
            for r in result:

                row_str = " | ".join(str(item) for item in r if item)
                formatted_rows.append(f"- {row_str}")

            rows = "\n".join(formatted_rows)
            #context = f"Database Query Result:\n{rows}"
            context = f"Database Query Result:\n" + rows.strip()
            
            if not formatted_rows:
                context = "Database Query Result: No records found."
                
            return {
            "context": context,
            "tool_type": "sql",
            "rows": result
        }
        except Exception as e:
            return {
            "context": f"SQL Execution Error: {str(e)}",
            "tool_type": "sql",
            "rows": []
        }

    else:
        print("DEBUG: Jumping into RAG...", flush=True)
        context = rag_db(question) if rag_db else "No RAG DB available."

    return context
    
# def execute_tool(question: str, rag_db=None):
#     """
#     Decides tool, executes it, and returns context for LLM.
#     """

#     decision = decide_tool_and_query(question)
#     context=""
#     print("TOOL SELECTED:", decision["tool"])
#     print("QUESTION:", question)

#     if decision["tool"] == "sql":
#         try:
#             print("Inside SQL Tool")
#             result = run_sql_query(decision["sql_query"])

#             print("RAW SQL RESULT TYPE:", type(result))
#             print("RAW SQL RESULT:", result)
            
#             formatted_rows = []
#             for r in result:

#                 row_str = " | ".join(str(item) for item in r if item)
#                 formatted_rows.append(f"- {row_str}")

#             rows = "\n".join(formatted_rows)
#             #context = f"Database Query Result:\n{rows}"
#             context = f"Database Query Result:\n" + rows.strip()
            
#             if not formatted_rows:
#                 context = "Database Query Result: No records found."
                
#             print("SQL Result processed successfully")
#         except Exception as e:
#             context = f"SQL Execution Error: {str(e)}"
#         #pass
#     else:
#         print("DEBUG: Jumping into RAG...", flush=True)
#         context = rag_db(question) if rag_db else "No RAG DB available."

#     return context
    
    
    
