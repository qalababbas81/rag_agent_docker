import pyodbc
from langchain.tools import tool

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=CS-DEV-QALAB\\MYSQLSERVER;"
    "DATABASE=DemoDB;"
    "Trusted_Connection=yes;"
)
# conn_str = (
#     "DRIVER={ODBC Driver 18 for SQL Server};"
#     "SERVER=sqlserver;"
#     "DATABASE=DemoDB;"
#     "UID=sa;"
#     "PWD=KSAcs321;"
#     "TrustServerCertificate=yes;"
# )

def run_sql_query(query: str):
    """
    Executes SQL query safely and returns results.
    """

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()
        results =[]
        for row in rows:
            results.append(tuple(row))

        # columns = [column[0] for column in cursor.description]

        # results = []
        # for row in cursor.fetchall():
        #     results.append(dict(zip(columns, row)))

        conn.close()

        return results

    except Exception as e:
        return f"SQL Error: {str(e)}"