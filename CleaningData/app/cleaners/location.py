import numpy as np 
from sqlalchemy import create_engine, text
import pandas as pd
from CleaningData.config.sqlacces import connection_str_dw_fz_g
from unidecode import unidecode
import re


departamento_dict = {
    'AMAZONAS': 3,
    'ANTIOQUIA': 1,
    'ARAUCA': 2,
    'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA': 3,
    'ATLÁNTICO': 3,
    'BOGOTÁ, D.C.': 0,
    'BOLÍVAR': 3,
    'BOYACÁ': 1,
    'CALDAS': 2,
    'CAQUETÁ': 2,
    'CASANARE': 2,
    'CAUCA': 2,
    'CESAR': 3,
    'CHOCÓ': 3,
    'CÓRODBA': 3,
    'CUNDINAMARCA': 1,
    'GUAINÍA': 3,
    'GUAVIARE': 2,
    'HUILA': 1,
    'LA GUAJIRA': 3,
    'MAGDALENA': 3,
    'META': 1,
    'NARIÑO': 3,
    'NORTE DE SANTANDER': 3,
    'PUTUMAYO': 3,
    'QUINDIO': 1,
    'RISARALDA': 1,
    'SANTANDER': 2,
    'SUCRE': 2,
    'TOLIMA': 2,
    'VALLE DEL CAUCA': 2,
    'VAUPÉS': 3,
    'VICHADA': 3
}

sabana = {
    'COTA': 0,
    'CHÍA': 0,
    'TENJO': 0,
    'TABIO': 0,
    'CAJICÁ': 0,
    'SOPÓ': 0,
    'TOCANCIPÁ': 0,
    'GACHANCIPÁ': 0,
    'ZIPAQUIRÁ': 0,
    'COGUA': 0,
    'NEMOCÓN': 0,
    'CALI' :1,
    'BARBOSA' : 1,
    'GIRARDOTA' : 1,
    'COPACABANA' : 1,
    'BELLO' : 1,
    'MEDELLÍN' : 1,
    'ENVIGADO' : 1,
    'ITAGÜÍ' : 1,
    'SABANETA' : 1,
    'LA ESTRELLA' : 1,
    'BOGOTÁ, D.C.': 0,
    'MADRID' : 0,
    'FUNZA' : 0,
    'MOSQUERA' : 0
}

class Location:

    @staticmethod 
    def _query_sql() -> str: 
        """
        Generate the SQL query to retrieve the average grade.

        Args:

        Returns:
            str: The SQL query.
        """

        query = """ 
                SELECT Mpios_MGN_Dane.MPIO_CNMBR, Mpios_MGN_Dane.DPTO_CNMBR
                ,[cdgop_int]
                ,[pob_dane_2025]
                ,[Hab_km2_2025]
                ,[Tp_Ru_2025],
                [Dim.Clas_Ruralidad]."Desc"
        FROM [Geoespacial].[dbo].[Proyecciones_Poblacion_Dane]
        LEFT JOIN [dbo].[Dim.Clas_Ruralidad] on [Proyecciones_Poblacion_Dane].Tp_Ru_2025 = [Dim.Clas_Ruralidad].Cod
        left join dbo.Mpios_MGN_Dane ON cast(Mpios_MGN_Dane.MPIO_CCNCT as int) = Proyecciones_Poblacion_Dane.cdgop_int
               """
        
        return query
    
    @staticmethod
    def rem2(text: str):
        replace_dict = {
            " d.c. ": ""
            # " el ": "",
            # " la ": "",
            # " de ": "",
            # " " : ""
        }
        def capitalize_after_space(text: str):
            return " ".join(word.capitalize() for word in text.split())
        # Convertir a minúsculas y eliminar tildes
        text = unidecode(str(text).lower().capitalize())
        text = capitalize_after_space(text)
        # Reemplazar según el diccionario
        for old, new in replace_dict.items():
            text = text.replace(old, new)

        return text

    @staticmethod
    def remplace(text: str):
        replace_dict = {
            "d.c.": "",
            "el": "",
            "la": "",
            "de": "",
            " ": ""
        }

        # Convertir a minúsculas y eliminar tildes
        text = unidecode(str(text).lower().capitalize())
        
        # Reemplazar según el diccionario
        for old, new in replace_dict.items():
            text = text.replace(old, new)
        
        text = re.sub(r"[.,]", "", text)

        return text

    @classmethod
    def tabla_territorio(cls):

        connect_str: str = connection_str_dw_fz_g
        engine = create_engine(connect_str)
        query = cls._query_sql()
        df = pd.read_sql(query, engine)
        engine.dispose()
        df = df.rename(columns={'cdgop_int' : 'MPIO_CDPMP'})
        df['Muni_Nom_Cruce'] = df['MPIO_CNMBR'].apply(cls.rem2)
        df['Nivel_Castigo'] = df['DPTO_CNMBR'].map(departamento_dict)
        df['nivel_tipo'] = df['Tp_Ru_2025'].map({1: 1, 2: 2, 3: 2, 4: 3})
        df['Nivel_Castigo'] = df[['Nivel_Castigo', 'nivel_tipo']].max(axis=1)

        for municipio, nuevo_nivel in sabana.items():
            df.loc[(df['MPIO_CNMBR'] == municipio) & (df['Nivel_Castigo'] > nuevo_nivel), 'Nivel_Castigo'] = nuevo_nivel
        
        df_zomac = pd.read_excel('/home/manueltorres/analitica-garaje/Gamas.xlsx', sheet_name='Zomac PDET')
        df_zomac['Zomac'] = df_zomac['Zomac'].map({'ZOMAC' : 1})
        df = df.merge(df_zomac[['MPIO_CNMBR', 'DPTO_CNMBR']], on=['MPIO_CNMBR', 'DPTO_CNMBR'], how='left', indicator=True)
        df.loc[df["_merge"] == "both", "Nivel_Castigo"] = 3  # Si está en df_zomac, asignar nivel 3
        df.drop(columns=["_merge", "nivel_tipo"], inplace=True) 

        df.to_csv('../municipios_punishment.csv', index=False)
        df.to_excel('../MPIOS_MGN_2021_Names.xlsx')

        return df
    
    
    
    @classmethod
    def location_punish(cls, df):
        
        df_pu = pd.read_csv('CleaningData/app/cleaners/municipios_punishment.csv')
    
        print(cls.remplace("BOGOTÁ, D.C."))
        df['Ubicacion_simple'] = df['Ubicacion'].apply(cls.remplace)
        # print(df[['Ubicacion', 'Ubicacion_simple']].head())

        df_pu['MPIO_CNMBR_simple'] = df_pu['MPIO_CNMBR'].apply(cls.remplace)

        df['Ubicacion_simple'] = df['Ubicacion_simple'].astype(str)
        df_pu['MPIO_CNMBR_simple'] = df_pu['MPIO_CNMBR_simple'].astype(str)
        df_pu['MPIO_CNMBR_simple'] = df_pu['MPIO_CNMBR_simple'].str.strip()
        df['Ubicacion_simple'] = df['Ubicacion_simple'].fillna('Bogota') 
        # print(df_pu[['MPIO_CNMBR', 'MPIO_CNMBR_simple', 'Nivel_Castigo']].head())
        df_pu = (
                    df_pu
                    .sort_values('Nivel_Castigo', ascending=False)
                    .drop_duplicates(subset='MPIO_CNMBR_simple', keep='first')
                )
        # print(df_pu['MPIO_CNMBR_simple'].value_counts().head(10))
        # dupes = df_pu['MPIO_CNMBR_simple'][df_pu['MPIO_CNMBR_simple'].duplicated(keep=False)]
        # print(dupes.unique())
        df = df.merge(df_pu[['MPIO_CNMBR_simple', 'Nivel_Castigo', 'MPIO_CDPMP']], left_on='Ubicacion_simple', right_on='MPIO_CNMBR_simple',how='left')
        df.drop(columns=["Ubicacion_simple", "MPIO_CNMBR_simple"], inplace=True) 
        df = df.rename(columns={'Nivel_Castigo' : 'Ubicacion_int'})
        
        return df

