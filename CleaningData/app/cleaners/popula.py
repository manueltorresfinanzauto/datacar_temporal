from sqlalchemy import create_engine, text
import pandas as pd
from CleaningData.config.sqlacces import connection_str_dw_fz, connection_str
import swifter

class Popularity:
    """ 
    Class that gives the popularity of a car
    """

    @staticmethod 
    def _query_sql(sele : int = 1) -> str: 
        """
        Generate the SQL query to retrieve the average grade.

        Args:

        Returns:
            str: The SQL query.
        """
        if sele == 1:
            query = """
                SELECT [Cod Fasecolda] as Cod_fasecolda
                    ,[Marca]
                    ,[Linea]
                    ,[Modelo]
                    ,[Calificacion]
                    FROM [Analitica].[opi].[Opinautos_Opiniones]
            """
            return query 
        
        if sele == 2:
            query = """
                SELECT 
                    Marca, 
                    AVG(CAST(Calificacion AS FLOAT)) AS Calificacion_promedio
                FROM 
                    [Analitica].[opi].[Opinautos_Opiniones]
                GROUP BY 
                    Marca
                ORDER BY 
                    Calificacion_promedio DESC;
            """
            return query



    @classmethod 
    def call_promedio_estrellas(cls):

        connect_str: str = connection_str
        engine = create_engine(connect_str)
        query = cls._query_sql(1)
        df = pd.read_sql(query, engine)
        engine.dispose()

            # Ensure Calificacion is numeric
        df["Calificacion"] = df["Calificacion"].astype(float)
        # df["Linea"] = df["Linea"].str.replace(r"\s*\[\d+\]", "", regex=True).str.lower().str.strip()
        df["Linea"] = (df["Linea"].str.replace(r"\s*\[\d+\]", "", regex=True)
                        .str.split().str[0]  # Esto toma solo la primera palabra
                        .str.lower()
                        .str.strip()
                    )
        df["Marca"] = df["Marca"].str.replace(r"\s*\[\d+\]", "", regex=True).str.lower().str.strip()

        # Compute average rating per (Cod Fasecolda, Modelo)
        df_avg = df.groupby(["Marca", "Linea"])["Calificacion"].mean().round(5).reset_index()
        df_avg.rename(columns={"Calificacion": "Promedio_estrellas"}, inplace=True)

        # df_avg["Modelo"] = df_avg["Modelo"].astype(int)
        # print(df_avg.head())  # Ensure data exists
        # print(df_avg.shape)   # Ensure it's not empty


        # Convert to dictionary for faster lookup
        avg_dict = df_avg.set_index(["Marca","Linea"])["Promedio_estrellas"].to_dict()

        return avg_dict   # Return dictionary for O(1) lookup speed
    
    @staticmethod
    def get_avg_rating_parallel(row, avg_dict):
        """Lookup function for parallel execution."""
        try:
            # Ensure keys are the correct type
            marca = row["_Marca_clean"]
            linea = row["_Linea_clean"]
            return avg_dict.get((marca, linea), None)  # O(1) lookup
        except KeyError as e:
            print(f"KeyError: {e} - Available columns: {row.index.tolist()}")
            return None
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None
        
    @classmethod
    def apply_avg_rating_parallel(cls, df_or):
        """Apply the rating lookup function in parallel using swifter."""
        avg_dict = cls.call_promedio_estrellas()
        print(list(avg_dict.items())[:5])  # Show first 5 key-value pairs

        df_or["_Linea_clean"] = (df_or["Linea"].str.replace(r"\s*\[\d+\]", "", regex=True)
                        .str.split().str[0]  # Esto toma solo la primera palabra
                        .str.lower()
                        .str.strip())
        df_or["_Marca_clean"] = df_or["Marca"].str.replace(r"\s*\[\d+\]", "", regex=True).str.lower().str.strip()

        df_or["Promedio_estrellas"] = df_or.apply(
            lambda row: cls.get_avg_rating_parallel(row, avg_dict), axis=1
        )

        df_or.drop(columns=["_Linea_clean", "_Marca_clean"], inplace=True)

        return df_or
    
    @classmethod
    def promedio_popu(cls, df_or):
        
        connect_str: str = connection_str
        engine = create_engine(connect_str)
        query = cls._query_sql(2)
        df = pd.read_sql(query, engine)
        engine.dispose()
        df['Marca'] = df['Marca'].astype(str).str.upper()
        
        df_merged = df_or.merge(df, on='Marca', how='left')
        df_merged['Promedio_estrellas'] = df_merged['Promedio_estrellas'].fillna(df_merged['Calificacion_promedio'])
        
        df_merged = df_merged.drop(columns=['Calificacion_promedio'])
        return df_merged