from sqlalchemy import create_engine, text
import pandas as pd
from CleaningData.config.sqlacces import connection_str_dw_fz
import requests
from tqdm import tqdm, tqdm_pandas

class TRM:

    @staticmethod
    def _query_sql() -> str: 
        """
        Generate the SQL query to retrieve the average grade.

        Args:

        Returns:
            str: The SQL query.
        """

        query = """ 
                SELECT [DD/MM/AAAA] as [Fecha_venta]
                        ,[TRM]
                    FROM [Analitica].[oikos].[inf_eco_diaria]
               """
        
        return query
    
    @classmethod
    def search_trm_sql(cls, df):
        connect_str: str = connection_str_dw_fz
        engine = create_engine(connect_str)
        query = cls._query_sql()
        df_trm = pd.read_sql(query, engine)
        engine.dispose()

        df_merged = df.merge(df_trm, left_on = 'Fecha_venta', right_on='Fecha_venta', how='left')
        # print(df_merged.info())
        return df_merged
    
    @staticmethod
    def get_trm_from_api(date):
        """Fetch TRM from the API for a given date."""
        base_url = "https://www.datos.gov.co/resource/ceyp-9c7c.json"
        query = f"?vigenciadesde={date.strftime('%Y-%m-%dT00:00:00.000')}"
        response = requests.get(base_url + query)

        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data['valor'])  # Return TRM value
        
        return None  # Return None if API fails
    
    @classmethod
    def apply_trm_logic(cls, df):
        """Apply TRM logic: use SQL values, but fetch from API if missing."""
        df = cls.search_trm_sql(df)
        # tqdm.pandas()
        # df['TRM'] = df.progress_apply(lambda row: row['TRM'] if pd.notna(row['TRM']) else cls.get_trm_from_api(row['Fecha_venta']), axis=1)
        return df
    
    
