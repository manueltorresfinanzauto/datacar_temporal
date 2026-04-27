from dotenv import load_dotenv
import os
import pyodbc
from urllib.parse import quote_plus

load_dotenv()
# --------------------------------------------------------------------------------------

connection_str = ""

# ...............................................................................................
# Coonection parameters for dw_fz
server = os.environ['DB_NAME_SERVER_FZ']  # e.g., 'localhost' or '192.168.1.100'
database = os.environ['DB_DATABASE_FZ']    # Name of your database
username = os.environ['DB_USER_FZ']
password = os.environ['DB_PASSWORD_FZ']
password = quote_plus(password)
driver = f'{pyodbc.drivers()[0]}'  # Ensure the correct driver is installed
connection_str_dw_fz = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"

# ...............................................................................................

connection_str_dw_fz_g = ""
