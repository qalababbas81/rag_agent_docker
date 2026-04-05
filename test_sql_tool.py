from tools.sql_tool import run_sql_query

query = "SELECT TOP 5 * FROM Employees"

result = run_sql_query(query)

print(result)