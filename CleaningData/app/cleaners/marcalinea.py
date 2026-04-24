from sqlalchemy import create_engine, text
import pandas as pd
from CleaningData.config.sqlacces import connection_str_dw_fz

class MarcaLinea:

    @staticmethod
    def _query_sql() -> str: 
        """
        Generate the SQL query to retrieve the average grade.

        Args:

        Returns:
            str: The SQL query.
        """

        query = """ 
                SELECT Codigo as Cod_fasecolda, Marca, Referencia1 as Linea, Referencia2, Referencia3

                    FROM [Analitica].[dbo].[COD_Fasecolda]
        """
        return query
    
    @classmethod
    def find_marcalinea(cls, df) -> pd.DataFrame:

        connect_str: str = connection_str_dw_fz
        engine = create_engine(connect_str)
        query = cls._query_sql()
        df_fase = pd.read_sql(query, engine)
        engine.dispose()

        df_merged = df.merge(df_fase, left_on = 'Cod_fasecolda', right_on='Cod_fasecolda', how='left')

        return df_merged