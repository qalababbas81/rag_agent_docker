from langchain_ollama import ChatOllama
from tools.sql_tool import run_sql_query


# def route_tool (tool_name, input_data):
#     if tool_name == "sql_query":
#         return run_sql_query(input_data)
#     else:
#         return {"error":"Tool not found"}
    
#llm = ChatOllama(model="llama3.1:latest", temperature=0)
llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0,
    base_url="http://ollama:11434"
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
You are a SQL assistant.
Convert this natural language request into a SQL query.
Database table: Employees(Id, Name, Email, Address, EmpImagePath).
Only return SQL, do not add explanations.
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
    print("TOOL SELECTED:", decision["tool"])
    print("QUESTION:", question)

    if decision["tool"] == "sql":
        try:
            result = run_sql_query(decision["sql_query"])
            formatted_rows = []

            for r in result:
                formatted_rows.append(
                    f"ID: {r[0]}, Name: {r[1]}, Email: {r[2]}, Address: {r[3]}"
                )
            #context = f"SQL Query Result:\n{result}"
            rows = "\n".join(formatted_rows)
            context = f"""
            Database Query Result:
            {rows}
            """
            print("SQL Result:", result)
        except Exception as e:
            context = f"SQL Execution Error: {str(e)}"
    else:
        context = rag_db(question) if rag_db else "No RAG DB available."

    return context
    
    
    
