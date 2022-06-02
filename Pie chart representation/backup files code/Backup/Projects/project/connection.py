import textwrap
import pyodbc

driver = '{ODBC Driver 17 for SQL Server}'

server_name = 'serverga'
database_name = 'people'

server = '{server_name}.database.windows.net,1433'.format(server_name=server_name)

username = "gaurav"
password = "admin02@azure"

connection_string = textwrap.dedent('''
    Driver={driver};
    Server={server};
    Database={database};
    Uid={username};
    Pwd={password};
    Encryt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
'''.format(
    driver=driver,
    server=server,
    database=database_name,
    username=username,
    password=password
))

cnxn: pyodbc.Connection = pyodbc.connect(connection_string)
crsr: pyodbc.Cursor = cnxn.cursor()
cnxn.close()