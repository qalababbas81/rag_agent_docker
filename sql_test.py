import pyodbc

# conn_str = (
#     "DRIVER={ODBC Driver 17 for SQL Server};"
#     "SERVER=CS-DEV-QALAB\MYSQLSERVER;"
#     "DATABASE=master;"
#     "Trusted_Connection=yes;"
# )
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=sqlserver;"
    "DATABASE=DemoDB;"
    "UID=sa;"
    "PWD=KSAcs321;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)

cursor = conn.cursor()

cursor.execute("SELECT name FROM sys.databases")

for row in cursor.fetchall():
    print(row)

conn.close()