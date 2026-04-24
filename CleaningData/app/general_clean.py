import pandas as pd 
from tqdm import tqdm
from datetime import datetime
from sqlalchemy import create_engine, text
import time 
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm, tqdm_pandas
import re
import unicodedata
from tqdm import tqdm
import numpy as np
import unicodedata
# Personal 
from CleaningData.app.cleaners.damage import VehicleDamage  
from CleaningData.app.Simul.simulate import Simulation_p_k, mean_km_f
from CleaningData.app.cleaners.search_code_faseco import Fasecol 
from CleaningData.app.cleaners.demand import Demanda
from CleaningData.app.cleaners.popula import Popularity
from CleaningData.app.cleaners.combus import Combustible
from CleaningData.app.cleaners.fasecol import tf_idf_assign
from CleaningData.app.cleaners.marcalinea import MarcaLinea
from CleaningData.app.macroecono.trm import TRM
from CleaningData.app.cleaners.gamas import Gamas
from CleaningData.app.cleaners.motos import Motos
from CleaningData.app.cleaners.location import Location
# from CleaningData.app.cleaners.damage import VehicleDamage
from CleaningData.app.cleaners.fasecol import tf_idf_assign
from CleaningData.app.Simul.simulate import Simulation_p_k

tqdm.pandas()

def clean_text(text):
    if pd.isna(text):
        return ''
    
    # Quitar tildes
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    
    # Pasar a minúsculas
    text = text.lower().capitalize()
    
    # Quitar puntuación y paréntesis, corchetes, llaves
    text = re.sub(r"[.,;:()\[\]{}]", "", text)
    
    # Quitar múltiples espacios
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def search_location(df):
    if 'Ubicacion' in df.columns:
        df['Ubicacion'] = df['Ubicacion'].fillna('Bogota')
    else:
        df['Ubicacion'] = 'Bogota'
        
    return df
def as_blin(df):
    df['Blindaje'] = 0
    return df

def damage_f(df):
    if 'Realiability' not in df.columns:
        df['Realiability'] = '100%'
        return df
    else:
        df['Realiability'] = df['Realiability'].fillna('100%')
        return df        


def linea_search(df):
    if 'Referencia' in df.columns:
        df[['Linea', 'Ref1']] = df['Referencia'].str.split(n=1, expand=True)
    return df
def vitrina(df):
    dic_vi = {'Vitrina' : 0, 'Venta Especial' : 1}
    if 'Estado_vitrina' in df.columns:
        df['Estado_vitrina'] = df['Estado_vitrina'].fillna('Vitrina')
        df['Estado_vitrina_int'] = df['Estado_vitrina'].map(dic_vi)
    else:
        df['Estado_vitrina'] = 'Vitrina'  
        df['Estado_vitrina_int'] = df['Estado_vitrina'].map(dic_vi)

    return df 

def servicios(df):
    dic_vi = {'Particular' : 0, 'Publico' : 1, 'Público' : 1}
    if 'Servicio' in df.columns:
        df['Servicio'] = df['Servicio'].apply(clean_text)
        df['Servicio'] = df['Servicio'].fillna('Particular')
        df['Servicio_int'] = df['Servicio'].map(dic_vi)
    else:
        df['Servicio'] = 'Particular'  
        df['Servicio_int'] = df['Servicio'].map(dic_vi)

    return df 

def estado_veh(df):
    dic_estado = {'Nuevos' : 0, 'Usados' : 1, 'Nuevo' : 0, 'Usado' : 1}
    if 'Estado_vehiculo' in df.columns:
        df['Estado_vehiculo_int'] = df['Estado_vehiculo'].map(dic_estado)
    else:
        df['Estado_vehiculo'] = 'Usados'
        df['Estado_vehiculo_int'] = df['Estado_vehiculo'].map(dic_estado)
    df['Estado_vehiculo_int'] = df['Estado_vehiculo_int'].fillna(1)
    return df

def combu(df):
    if 'Combustible' in df.columns:
    # print(df_v2.info())
        Combustible.combus_short(df)
        df.loc[(df['Combustible'].isnull() | (df['Combustible'] == '')), 'Combustible'] = 'GSL'
        Combustible.combus_number(df)
        return df
    else:
        df = Combustible.search_combus(df)
        df.loc[(df['Combustible'].isnull() | (df['Combustible'] == '')), 'Combustible'] = 'GSL'
        Combustible.combus_number(df)
        return df
    
def limpiar_texto(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return texto.lower().capitalize()

def max_cleaner(df):
    
    df.columns = [limpiar_texto(col) for col in df.columns]

     # Diccionario de mapeo de nombres de columna
    column_map = {
        'Cod_fasecolda': ['Codigo fasecolda', 'Codigo_fasecolda', 'Codigo', 'codigo_fasecolda', 'codigo fasecolda', 'Codigofasecolda'],
        'Descripcion': ['Observaciones'],
        'Fecha_venta': ['Fecha del pricing', 'Fecha de pricing', 'Fecha pricing', 'Fecha de inspección', 'Fecha de inspeccion', 'Fecha de inspección', 'Fecha insercion', 'Fecha inserción', 'Fecha', 'Fecha proceso', 'Fecha_proceso'],
        'Pricing': ['Precio', 'PRECIO VENTA', 'PRECIO_VENTA', 'PRECIO_VENTA', 'Precio_venta', 'Precio venta'], 
        'Descripcion' : ['Observaciones'], 
        'Estado_vehiculo' : ['Estado', 'Estado_venta'],
        'Modelo' : ['ANIO_MODELO', 'ANIO MODELO', 'Anio_modelo', 'Anio modelo'],
        'Ubicacion' : ['Ciudade matricula', 'ciudad de matricula']
    }
    print(df.shape)
    # Renombrar columnas basadas en los posibles nombres
    for standard_name, possible_names in column_map.items():
        for possible_name in possible_names:
            if possible_name in df.columns:
                df.rename(columns={possible_name: standard_name}, inplace=True)
                break
    print(df.columns.tolist())
    print('Remove motos')

    # df = Motos.find_motos(df)
    # df = df.dropna(subset=['Cod_fasecolda'])
    df['Cod_fasecolda'] = df['Cod_fasecolda'].fillna(99999999)
    print(df.shape)
    df["Cod_fasecolda"] = df["Cod_fasecolda"].astype(int)

    
    
    # Verificar columnas faltantes y aplicar funciones de generación
    required_columns = {
        'Cod_fasecolda': tf_idf_assign.marca_cofc,
        'Ubicacion': search_location,
        'Blindaje' : as_blin,
        'Marca' : tf_idf_assign.marca_linea_ref,
        'Linea' : linea_search
    }
    
    for col, func in required_columns.items():
        if col not in df.columns:
            print(col)
            df = func(df)
            print(df.shape)

    print('Applying location')
    print(df.columns)

    df = search_location(df) 
    print(df.shape)
    df = Location.location_punish(df)
    print(df.shape)
    


    print('Applying estado')
    df = estado_veh(df)
    print(df.shape)


    print('Applying kilometraje')
    if 'Kilometraje' not in df.columns:
        df['Kilometraje'] = np.nan
    mask = df['Kilometraje'].isna()

    df.loc[mask, 'Kilometraje'] = df.loc[mask].apply(
                                    lambda row: mean_km_f(row['Modelo'], row['Estado_vehiculo'], row['Fecha_venta']), axis=1)

    print(df.shape)

    print('Applying gamma')
    df = Gamas.find_gamma(df)
    df = Gamas.add_gamma_mode(df)
    df = Gamas.fill_nans_gammas(df)
    print(df.shape)

    print('Applying demanda')
    df = Demanda.search_demanda(df)
    df = df.rename(columns={'Percentage' : 'Demanda'})
    df.loc[df['Demanda'].isnull(), 'Demanda'] = 0.0
    print(df.shape)

    # print('Applying popularity')

    # df = Popularity.apply_avg_rating_parallel(df)
    # df = Popularity.promedio_popu(df)
    # df['Promedio_estrellas'] = df['Promedio_estrellas'].fillna(3.92)
    # print(df.shape)    
    
    print('Applying vitrina')
    df = vitrina(df)
    print(df.shape)

    print('Applying servicios')
    df = servicios(df)
    print(df.shape)

    print('Applying combustible')

    df = combu(df)
    print(df.shape)

    print('Damage')
    df = damage_f(df)
    df = VehicleDamage.percentage_damage(df)
    
    print(df.shape)
    
    df['Year'] = df['Fecha_venta'].dt.year
    df['Month'] = df['Fecha_venta'].dt.month
    df = df.dropna(subset=['Cod_fasecolda'])


    print(df.columns.tolist())

    selected_columns = ['Placa','Cod_fasecolda', 'Marca', 'Linea', 'Ref1', 'Referencia', 'Modelo', 'Kilometraje', 'Fecha_venta', 'Year', 'Month','Ubicacion', 'Ubicacion_int', 'Demanda', 'Combustible', 'Combustible_int','Descripcion', 'Descripcion_int', 'Gama', 'Gama_int', 'Blindaje', 'Estado_vehiculo', 'Estado_vehiculo_int', 'Servicio', 'Servicio_int', 'Estado_vitrina', 'Estado_vitrina_int','Pricing']
    df = df[[col for col in selected_columns if col in df.columns]]
    

    return df



