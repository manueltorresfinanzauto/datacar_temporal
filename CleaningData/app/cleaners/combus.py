from sqlalchemy import create_engine, text
import pandas as pd
from CleaningData.config.sqlacces import connection_str_dw_fz, connection_str

class Combustible:

    @staticmethod
    def _query_sql() -> str: 
        """
        Generate the SQL query to retrieve the average grade.

        Args:

        Returns:
            str: The SQL query.
        """

        query = """ 
                SELECT Codigo, Combustible
                    FROM [Analitica].[dbo].[COD_Fasecolda]
               """
        
        return query
    
    @classmethod
    def search_combus(cls, df):
        connect_str: str = connection_str_dw_fz
        engine = create_engine(connect_str)
        query = cls._query_sql()
        df_fase = pd.read_sql(query, engine)
        engine.dispose()
        df["Cod_fasecolda"] = df["Cod_fasecolda"].astype(int)  
        df_fase["Codigo"] = df_fase["Codigo"].astype(int)
        df_fase = df_fase.rename(columns={'Codigo': 'Cod_fasecolda'})  # Ensure column names match before merging
        
        df_fase_unique = df_fase.groupby('Cod_fasecolda', as_index=False).first()
        df_merged = df.merge(df_fase_unique, on='Cod_fasecolda', how='left')

        # print(df_merged.info())
        return df_merged

    @staticmethod
    def combus_number(df):
        dic_comb = {'GSL':0,
                    'GAS':1,
                    'DSL':2,
                    'ELT':3,
                    'HBD':4}
        df['Combustible_int'] = df['Combustible'].map(dic_comb)

    @staticmethod
    def combus_short(df):
        dic_c = {'Gasolina': 'GSL',
                 'Diesel': 'DSL',
                 'Hibrido': 'HBD',
                 'GAS': 'GAS',
                 'Electrico': 'ELT'
                 }
        df['Combustible'] = df['Combustible'].map(dic_c)
        