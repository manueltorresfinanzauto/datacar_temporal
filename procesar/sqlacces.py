from dotenv import load_dotenv
import os
import pyodbc
from urllib.parse import quote_plus

load_dotenv()

# ...............................................................................................
# Coonection parameters for dw_fz
server = os.environ['DB_NAME_SERVER_FZ']  # e.g., 'localhost' or '192.168.1.100'
database = os.environ['DB_DATABASE_FZ']    # Name of your database
username = os.environ['DB_USER_FZ']
password = os.environ['DB_PASSWORD_FZ']
password = quote_plus(password)
driver = f'{pyodbc.drivers()[0]}' 
connection_str_dw_fz = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"
