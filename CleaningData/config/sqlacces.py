from dotenv import load_dotenv
import os
import pyodbc
from urllib.parse import quote_plus

load_dotenv()
# --------------------------------------------------------------------------------------
# Connection parameters for .17 
server = os.environ['DB_NAME_SERVER']  # e.g., 'localhost' or '192.168.1.100'
database = os.environ['DB_DATABASE']    # Name of your database
username = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
password = quote_plus(password)
driver = f'{pyodbc.drivers()[0]}'  # Ensure the correct driver is installed
connection_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"

# ...............................................................................................
# Coonection parameters for dw_fz
server = os.environ['DB_NAME_SERVER_FZ']  # e.g., 'localhost' or '192.168.1.100'
database = os.environ['DB_DATABASE_FZ']    # Name of your database
username = os.environ['DB_USER_FZ']
password = os.environ['DB_PASSWORD_FZ']
password = quote_plus(password)
connection_str_dw_fz = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"

# ...............................................................................................
# Coonection parameters for dw_fz geoespacial
server = os.environ['DB_NAME_SERVER_FZ_G']  # e.g., 'localhost' or '192.168.1.100'
database = os.environ['DB_DATABASE_FZ_G']    # Name of your database
username = os.environ['DB_USER_FZ_G']
password = os.environ['DB_PASSWORD_FZ_G']
password = quote_plus(password)
connection_str_dw_fz_g = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"
