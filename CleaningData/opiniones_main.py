import pandas as pd
from app.webscraping.opinautos_wsp import WebScrapinOpinautosOpiniones
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import pyodbc
from urllib.parse import quote_plus

load_dotenv()

def query_sql() -> str:
        """
        Generate the SQL query to retrieve the average grade
        Args:

        Returns:
            str: The SQL query
        """
        query  = """ 
                SELECT *
                FROM [Analitica].[pri].[base_vehiculos_v2]
                WHERE COMPANIA NOT IN ('Carfiao', 'Asousados') and MARCA='AUDI';
                """
        return query


# Connection parameters for .17 
server = os.environ['DB_NAME_SERVER']  # e.g., 'localhost' or '192.168.1.100'
database = os.environ['DB_DATABASE']    # Name of your database
username = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
password = quote_plus(password)
driver = f'{pyodbc.drivers()[0]}'  # Ensure the correct driver is installed
connection_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes"

connect_str: str = connection_str
engine = create_engine(connect_str)
query = query_sql()
df = pd.read_sql(query, engine)
engine.dispose()


df = df.rename(columns={'ANIO_MODELO' : 'ID_FacecoldaModelo', 'MARCA' : 'marca', 'LINEA' : 'linea', 'COD_FASECOLDA' : 'cod fasecolda', })

# print(df.columns.tolist())

opinione = WebScrapinOpinautosOpiniones()
df = pd.DataFrame({
    'marca': ['mazda'],
    'linea': ['3'],
    'cod fasecolda': ['5604003'],
    'ID_FacecoldaModelo': '2020'
})

opinione.opinautos_opiniones(df)