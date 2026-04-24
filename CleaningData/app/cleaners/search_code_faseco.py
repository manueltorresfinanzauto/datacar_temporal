from sqlalchemy import create_engine, text
import pandas as pd
from CleaningData.config.sqlacces import connection_str_dw_fz

class Fasecol:
    """
    Class to find the "codigo fasecolda" from the Marca, Linea, and Referencia
    """

    @staticmethod
    def _query_sql() -> str:
        """
        Generate the SQL query to retrieve the average grade
        Args:

        Returns:
            str: The SQL query
        """
        query = """ 
                SELECT DISTINCT [Codigo]
                FROM [Analitica].[dbo].[COD_Fasecolda]
                where Marca = :Marca and Referencia1 = :Referencia1 and Referencia2 = :Referencia2
                """
        return query
    
    @classmethod
    def search_score(cls, Marca: str, Referencia1: str, Referencia2: str) -> int:
        """
        Will be search for the score value of the car in my input 

        Args:
            Marca (str) : The brand name 
            Referencia1 (str) : Model name (this is not the year)
            Referencia2 (str) : An extra reference of the model 

        """
        connect_str: str = connection_str_dw_fz
        engine = create_engine(connect_str)
        query = cls._query_sql()
        with engine.connect() as connection:
            try:
                result = connection.execute(text(query), {'Marca' : Marca
                                                        , 'Referencia1' : Referencia1
                                                        , 'Referencia2' : Referencia2})
                result_score = result.fetchone()
            except TypeError as e:
                print(f"Error: Valores invalidos o faltan valores - {e}")

        
        engine.dispose()

        return result_score[0] if result_score else None