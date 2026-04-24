import pandas as pd 
import numpy as np
from procesar.sqlacces import connection_windows_dw_fz
from sqlalchemy import create_engine, text
from datetime import datetime
import re
from typing import Optional
from sqlalchemy.engine import Engine
from unidecode import unidecode
import pandas as pd
from sqlalchemy import create_engine
import pyodbc


class Gamas:

    @staticmethod
    def call_df_gama():
        # df_g = pd.read_excel('CleaningData/app/cleaners/Gamas.xlsx', sheet_name='Gamas 343')
        connect_str: str = connection_windows_dw_fz
        engine = create_engine(connect_str)
        query = 'SELECT * FROM [Analitica].[pri].[Gamas]'
        df_g = pd.read_sql(query, engine)
        engine.dispose()
        return df_g
    
    @classmethod
    def find_gamma(cls, df):
        df_g = cls.call_df_gama()
        df_g["Codigo"] = df_g["Codigo"].astype(int)
        df = df.merge(df_g[['Codigo', 'Criterio Percepción ']], left_on='Cod_fasecolda', right_on='Codigo', how='left')
        df = df.rename(columns={'Criterio Percepción ' : 'Gama'})
        dic_g = {'De Lujo ': 4, 'Gama Alta' : 3, 'Gama Media' : 2, 'Gama Baja' : 1}
        df['Gama_int'] = df['Gama'].map(dic_g)
        return df
    
    @staticmethod
    def safe_mode(series):
        mode_vals = series.mode()
        if not mode_vals.empty:
            return mode_vals.iloc[0]
        else:
            return np.nan  # o cualquier valor por defecto

    @classmethod
    def dic_gama(cls):
        df_g = cls.call_df_gama()

        dic_g = {'De Lujo ': 4, 'Gama Alta': 3, 'Gama Media': 2, 'Gama Baja': 1}
        reverse_dic_g = {v: k for k, v in dic_g.items()} 
        df_g['Gama_int'] = df_g['Criterio Percepción '].map(dic_g)
        # most_common = df_g.groupby('Marca')['Gamma_int'].agg(lambda x: x.mode()[0])
        most_common = df_g.groupby('Marca')['Gama_int'].agg(cls.safe_mode)
        dict_output = most_common.map(reverse_dic_g).to_dict()

        return dict_output

    @classmethod
    def add_gamma_mode(cls, df_2):
        
        dic_g = {'De Lujo ': 4, 'Gama Alta': 3, 'Gama Media': 2, 'Gama Baja': 1}

        dict_output = cls.dic_gama()
        dict_output  = {
                    k.lower().capitalize(): v
                    for k, v in dict_output.items()
                    }
        print(dict_output)
        # df_2['Gamma'] = df_2.apply(lambda row: dict_output[row['Marca']] if pd.isna(row['Gamma']) else row['Gamma'], axis=1)
        df_2['Gama'] = df_2.apply(lambda row: dict_output.get(row['Marca'], np.nan) if pd.isna(row['Gama']) else row['Gama'], axis=1)

        # Map Gamma to Gamma_int
        df_2['Gama_int'] = df_2['Gama'].map(dic_g)

        return df_2
    
    @classmethod
    
    def fill_nans_gammas(cls, df):
        dic_g = {'De Lujo ': 4, 'Gama Alta': 3, 'Gama Media': 2, 'Gama Baja': 1}

        df['Gama'] = df['Gama'].fillna('Gama Media')  
        df['Gama_int'] = df['Gama'].map(dic_g)

        return df

class Demanda:
    """ 
    Class that gives the demanda of the car 
    """
    @staticmethod
    def _query_sql() -> str:
        """
        Generate the SQL query to retrieve the average grade
        Args:

        Returns:
            str: The SQL query
        """
        query  = text(''' select * from [Analitica].[pri].[demanda_vehiculos] 
                ''')
        return query    

    
    @staticmethod
    def clean_text(text):
        """Removes special characters, extra spaces, and bracketed content like '[2]'."""
        if isinstance(text, str):
            text = re.sub(r"\[.*?\]", "", text)  # Remove anything inside brackets, including the brackets
            text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Keep only letters, numbers, and spaces
            text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
            return text.upper()  # Ensure case consistency
        return text 
    
    @classmethod
    def search_demanda(cls, df_or) -> pd.DataFrame: 
        """
        Will search for the demand percentage value of the car in my input 

        Args:
            df (pd.DataFrame): Input DataFrame with N columns. 

        Return:
            df_merged (pd.DataFrame): Input DataFrame with N columns.
        """
        # Marca = Marca.upper(); Linea = Linea.upper()
        connect_str: str = connection_windows_dw_fz
        engine = create_engine(connect_str)
        query = cls._query_sql()
        print('-------------------........................ calling the query')
        df = pd.read_sql(query, engine)
        engine.dispose()
        print('-------------------........................ changing types')
    
        df["Marca"] = df["Marca"].astype(str)
        df_or["Marca"] = df_or["Marca"].astype(str)
        df["Linea"] = df["Linea"].astype(str)
        df_or["Linea"] = df_or["Linea"].astype(str)
        df["Group_number"] = df["Group_number"].astype(float).astype(int)

        today = datetime.today()

        # First day of the current month
        first_day_of_month = datetime(today.year, today.month, 1)
        print('-------------------........................ group numbers')
        
        df_or['Group_number'] = (((first_day_of_month.year - df_or['Fecha_de_Inspeccion'].dt.year) * 12 + 
                       (first_day_of_month.month - df_or['Fecha_de_Inspeccion'].dt.month)) / 12 + 1).astype(int)
        # df_or.to_csv('out.csv', index=False)
        print('-------------------........................ strips')

        df_or["Marca"] = df_or["Marca"].str.strip()
        df["Marca"] = df["Marca"].str.strip()
        df_or["Linea"] = df_or["Linea"].str.strip()
        df["Linea"] = df["Linea"].str.strip()
        df_or["Marca"] = df_or["Marca"].str.upper()
        df["Marca"] = df["Marca"].str.upper()
        df_or["Linea"] = df_or["Linea"].str.upper()
        df["Linea"] = df["Linea"].str.upper()
        df_or["Linea"] = df_or["Linea"].apply(cls.clean_text)
        df["Linea"] = df["Linea"].apply(cls.clean_text)

        for col in ["Marca", "Linea"]:
            for df_name, dataframe in [("df_or", df_or), ("df", df)]:
                # Check for NaN or empty strings
                if dataframe[col].isna().any() or (dataframe[col].astype(str).str.strip().eq("")).any():
                    print(f"ERROR: Empty or NaN values found in {df_name}['{col}']")
                    print("Does not exist, check the codigo fasecolda")
                    print("Problematic values:")
                    print(dataframe[dataframe[col].isna() | (dataframe[col].astype(str).str.strip().eq(""))][col].unique())
                    raise ValueError(f"Invalid data in {df_name}['{col}'] - contains empty or NaN values")

        try:
            print('-------------------........................ try')
        
            # df_merged = df_or.merge(df[['Group_number', 'Marca', 'Linea', 'Percentage', 'Sales']], on=['Group_number', 'Marca', 'Linea'], how='left')
            df_single = df.groupby(['Group_number', 'Marca', 'Linea'], as_index=False).first()
            df_merged = df_or.merge(df_single[['Group_number', 'Marca', 'Linea', 'Percentage', 'Sales']], on=['Group_number', 'Marca', 'Linea'], how='left')
            return df_merged
        except KeyError as e:
            print(f'La entrada no coinciden, revisa los valores insertados - {e}')
    
        
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

def location_punish(df):
        
        # df_pu = pd.read_csv('CleaningData/app/cleaners/municipios_punishment.csv')
        connect_str: str = connection_windows_dw_fz
        engine = create_engine(connect_str)
        query = "SELECT * FROM [Analitica].[pri].[municipios_punishment]"
        df_pu = pd.read_sql(query, engine)
        engine.dispose()
    
        df['Ubicacion_simple'] = df['Ciudad_matrícula'].apply(remplace)
        # print(df[['Ubicacion', 'Ubicacion_simple']].head())

        df_pu['MPIO_CNMBR_simple'] = df_pu['MPIO_CNMBR'].apply(remplace)

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




marcas_chinas_colombia = [
    "BYD",
    "Chery",
    "JAC",
    "Foton",
    "JMC",
    "Changan",
    "DFSK",
    "Great Wall",
    "Haval",
    "MG",
    "Seres",
    "Zeekr",
    "Dongfeng",
    "BAIC",
    "Zotye",
    "FAW",
    "Bestune",
    "Changhe",
    "Mahindra"
]

marcas_chinas = [remplace(x) for x in marcas_chinas_colombia]

marcas_se = [
    "Chery",
    "JMC",
    "Changan",
    "DFSK",
    "Haval",
    "MG",
    "Seres",
    "Dongfeng",
    "BAIC",
    "Zotye",
    "FAW",
    "Bestune",
    "Changhe",
    "Mahindra",
]



marcas_se_2 = [remplace(x) for x in marcas_se]  

dict_est = {1 : 'Fuera de Estandar',
            2 : 'Semi Estandar',
            3 : 'Estandar'}

def precio_faseco(row):
    cod = row['Codigo_fasecolda']
    marca = row['Marca']
    modelo = row['Modelo']
    km = row['Kilometraje']
    ubi = row['Ubicacion_int']
    valor_ali = row['Valor_alistamiento']
    gama = row['Gama_int']
    demanda = row['Percentage']
    precio = row['Precio_DataCarro']

    marca_simple = remplace(marca)
    estado = 2
    if km > 95000:
        
        if km <= 140000:
            if modelo >=2011 and modelo <= 2014:
                estado = 2
                if marca_simple in marcas_chinas:
                    estado = 1
                if valor_ali >= precio*0.2:
                    estado = 2
            elif modelo < 2011:
                estado = 1                
        else:
            estado = 1
            
    else: 
        if modelo >= 2015:
            estado = 3 
            if gama == 4 or gama == 3:
                estado =2 
            if marca_simple in marcas_se_2:
                estado = 2 
            if valor_ali >= precio*0.2:
                estado = 2
       
        elif modelo >=2011 and modelo <= 2014:
            estado = 2
            if marca_simple in marcas_chinas:
                estado = 1
            elif demanda <= 0.0:
                estado = 1
            
        else:
            estado = 1

        

    if ubi == 3:
        estado = 1
    if valor_ali >= precio*0.2:
        estado = 1

    # print(cod,year)
    return dict_est[estado]


lista_col : list[str] = ['Placa', 'Marca', 'Linea', 'Referencia', 'Motorización', 'Clase_Vehículo', 'Modelo', 'Combustible', 'Tranmision', 'Kilometraje', 'Codigo_fasecolda', 'Color', 'Ciudad_matrícula', 'Servicio', 'Proceso', 'Valor_Recibido_Vehículo', 'Saldo_a_capital_Hoy', 'Saldo_a_capital_antes_de_Dacion', 'Valor_antes_de_la_aplicacion_de_la_deuda', 'Dias_en_Finanzauto', 'Polizas', 'Siniestros', 'Estado', 'Ubicacion_Vehiculo', 'Inspeccion', 'Inspeccionado_por', 'Observaciones', 'Valor_alistamiento', 'Fecha_de_Inspeccion', 'Valor_Alistamiento_Dacion', 'Reclamo_total', 'Precio_DataCarro', 'Precio_Maximo', 'Precio_Minimo', 'Comentario_Pricing', 'Fecha_Precio_DataCarro', 'Precio_comite', 'Comentario_Comite', 'Distribucion', 'Estado_Vehiculo', 'Fecha_Comite', 'Version_DataCarro', 'Valor_fasecolda', 'Guia_fasecolda']


list2 = ['Fecha', 'Inspeccionado por', 'document',  'Ubicación Vehículo', 'Origen_solicitud', 'Clase Vehículo', 'Placa', 'Marca_x', 'Linea', 'Modelo', 'Kilometraje', 'Servicio', 'Combustible ', 'Tranmision', 'Color', 'Motorización  / Tipo de Vehículo',  'Codigo fasecolda', 'Valor fasecolda', 'vehicleInformation_clientValue', 'Ciudad matrícula',  'Valor alistamiento', 'Observaciones',  'Valor Fasecolda Guia', 'Marca_y', 'Referencia1', 'Referencia2', 'Referencia3', 'TipoCaja', 'Clase', 'Version_GFC', 'Transmision', 'Precio_DataCarro', 'Precio_Maximo', 'Precio_Minimo', 'Cod_fasecolda', 'Placa.1', 'Fecha_Precio_DataCarro', 'Version_DataCarro']

dic_col = {'Fecha' : 'Fecha_de_Inspeccion', 'Referencia2' : 'Referencia', 'Marca_x' : 'Marca', 'Combustible ' : 'Combustible', 'Motorización  / Tipo de Vehículo' : 'Motorización' , 'Codigo fasecolda' : 'Codigo_fasecolda', 'Valor Fasecolda Guia' : 'Valor_fasecolda', 'Valor alistamiento' : 'Valor_alistamiento', 'Comments' : 'Comentario_Pricing', 'Version_GFC' : 'Guia_fasecolda', 'Ciudad matrícula' : 'Ciudad_matrícula', 'Pricing_DataCarro' : 'Precio_DataCarro'}


def main_estandar(df):
    df = df.rename(columns=dic_col)

    # l2 = [x for x in lista_col if x in df.columns.to_list()]
    # print(l2)
    df = Gamas.find_gamma(df)
    print('************************************************************')
    print(df.columns.to_list())
    df = Demanda.search_demanda(df)

    df = location_punish(df)

    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(df.columns.to_list())

    df['Estado_Vehiculo'] = df.apply(precio_faseco, axis=1)

    df['Fecha_de_Inspeccion'] = pd.to_datetime(df['Fecha_de_Inspeccion'], format='%d/%m/%Y')
    df['Fecha_Precio_DataCarro'] = pd.to_datetime(df['Fecha_Precio_DataCarro'], format='%d/%m/%Y')
    # Origen_solicitud

    df_brdp = df[(df['Origen_solicitud'] == 'BDRP') | (df['Origen_solicitud'] == 'Me lo Llevo')]

    df_grc = df[df['Origen_solicitud'] == 'GRC']



    server = '192.168.50.38\\DW_FZ'
    database = 'Analitica'
    schema_name = 'pri'
    table_name = 'pricing_brdp'
    DRIVER = f'{pyodbc.drivers()[3]}'


    engine = create_engine(f'mssql+pyodbc://{server}/{database}?driver={DRIVER}')
    query1 = f'SELECT top(1) * FROM {database}.{schema_name}.{table_name}'

    df_col = pd.read_sql(query1, engine)
    list_col : list = df_col.columns.to_list()
    list2 = [x for x in list_col if x in df.columns.to_list()]
    df_up = df_brdp[list2]

    df_up.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
    print("done!!")

    # ------------------------------------------------------------------------------------------

    table_name2 = 'pricing_grc'

    query1 = f'SELECT top(1) * FROM {database}.{schema_name}.{table_name2}'

    df_col = pd.read_sql(query1, engine)
    list_col : list = df_col.columns.to_list()
    list2 = [x for x in list_col if x in df.columns.to_list()]
    df_up = df_grc[list2]

    df_up.to_sql(table_name2, engine, schema=schema_name, if_exists='append', index=False)
    engine.dispose()
    print("done!!")



if __name__ == '__main__':

    # cargar el excel -------------------------------------------------
    df = pd.read_excel('brdp_24_04_2026.xlsx')
    main_estandar(df)
