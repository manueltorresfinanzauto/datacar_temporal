import pandas as pd 
from tqdm import tqdm
from datetime import datetime
from sqlalchemy import create_engine, text
import time 
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm, tqdm_pandas
import re
import unicodedata

# Personal 
from CleaningData.app.cleaners.punishment_damage import VehicleDamage  
from CleaningData.app.Simul.simulate import Simulation_p_k, mean_km_f, generate_simulated_data
from CleaningData.app.cleaners.search_code_faseco import Fasecol 
from CleaningData.app.cleaners.demand import Demanda
from CleaningData.app.cleaners.popula import Popularity
from CleaningData.app.cleaners.combus import Combustible
from CleaningData.app.cleaners.fasecol import tf_idf_assign
from CleaningData.app.cleaners.marcalinea import MarcaLinea
from CleaningData.app.macroecono.trm import TRM
from CleaningData.config.sqlacces import connection_str
from CleaningData.app.cleaners.location import Location
from CleaningData.app.cleaners.gamas import Gamas
from CleaningData.app.Simul.damage_score import simulate_damages
from CleaningData.app.cleaners.motos import Motos

def query_sql(fecha:str) -> str:
        """
        Generate the SQL query to retrieve the average grade
        Args:

        Returns:
            str: The SQL query
        """
        query  = f""" 
                SELECT *
                FROM [Analitica].[pri].[base_vehiculos_v2]
                WHERE COMPANIA NOT IN ('Carfiao', 'Asousados') AND Fecha_venta > '{fecha}';
                """
        return query

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

def vitrina(df):
    dic_vi = {'Vitrina' : 0, 'Venta Especial' : 1}
    if 'Estado_vitrina' in df.columns:
        df['Estado_vitrina'] = df['Estado_vitrina'].fillna('Vitrina')
        df['Estado_vitrina_int'] = df['Estado_vitrina'].map(dic_vi)
    else:
        df['Estado_vitrina'] = 'Vitrina'  
        df['Estado_vitrina_int'] = df['Estado_vitrina'].map(dic_vi)

    return df 

def v2_clean(fecha:str) -> None:
    connect_str: str = connection_str
    engine = create_engine(connect_str)
    query = query_sql(fecha)
    df_v2 = pd.read_sql(query, engine)
    engine.dispose()
    print(df_v2.shape)
    df_v2.loc[df_v2['ESTADO_VENTA'] == 'Nuevos', 'KILOMETRAJE'] = 0
    df_v2.loc[df_v2['COD_FASECOLDA'].isnull(), 'COD_FASECOLDA'] = df_v2['COD_FASECOLDA_APROX']
    df_v2.columns = [col.lower().capitalize() for col in df_v2.columns]
    df_v2 = df_v2.rename(columns={'Precio_venta' : 'Precio', 'Anio_modelo' : 'Modelo', 'Estado_venta' : 'Estado_vehiculo', 'Marca' : 'Marca_or', 'Linea' : 'Linea_or'})
    df_v2 = df_v2.rename(columns={'Marca_fasecolda' : 'Marca', 'Referencia1_fasecolda' : 'Linea', 'Anio_modelo' : 'Modelo', 'Precio': 'Pricing'})
    df_v2['Year'] = df_v2['Fecha_venta'].dt.year
    df_v2['Month'] = df_v2['Fecha_venta'].dt.month
    df_v2["Cod_fasecolda"] = df_v2["Cod_fasecolda"].astype(int)
    # print(df_v2.info())

    df_v2.loc[(df_v2['Kilometraje'] != 0) & (df_v2['Estado_vehiculo'].isnull() | (df_v2['Estado_vehiculo'] == '')), 'Estado_vehiculo'] = 'Usados'



    # print('Search cod fasecolda')
    # df_filas_sin_codigo = df_v2[df_v2["Cod_fasecolda"].isna() | (df_v2["Cod_fasecolda"] == '')].copy()
    # df_actua = Fasecol.marca_cofc(df_filas_sin_codigo)
    # df_actua = df_v2.rename(columns={'cod_fasecolda' : 'Cod_fasecolda'})
    # df_v2.update(df_actua['Cod_fasecolda'])


    print('Remove motos')

    df_v2 = Motos.find_motos(df_v2)
    # df_v2 = Simulation_p_k(df_v2)

    print('Applying location')

    df_v2['Ubicacion'] = 'Bogota' 
    df_v2 = Location.location_punish(df_v2)
    df_v2 = df_v2.rename(columns={'Nivel_Castigo' : 'Ubicacion_int'})
    print(df_v2.shape)

    print('Applying servicios')
    df_v2 = servicios(df_v2)
    print('Applying vitrina')
    df_v2 = vitrina(df_v2)
    print('Applying gamma')
    df_v2 = Gamas.find_gamma(df_v2)
    df_v2 = Gamas.add_gamma_mode(df_v2)
    df_v2 = Gamas.fill_nans_gammas(df_v2)

    print(df_v2.shape)

    print('Applying demanda')
    df_v2 = Demanda.search_demanda(df_v2)
    df_v2 = df_v2.rename(columns={'Percentage' : 'Demanda'})
    df_v2.loc[df_v2['Demanda'].isnull(), 'Demanda'] = 0.0
    print(df_v2.shape)

    # print(list(df_v2.columns))
    # print(df_v2['Cod_fasecolda'].head())

    # TODO: revisar de nuevo este de popularidad
    # NOTE: En esas estoy 

    print('Applying popularity')

    df_v2 = Popularity.apply_avg_rating_parallel(df_v2)
    df_v2 = Popularity.promedio_popu(df_v2)
    df_v2['Promedio_estrellas'] = df_v2['Promedio_estrellas'].fillna(3.92)
    print(df_v2.shape)

    print('Applying combustible')

    df_v2 = Combustible.search_combus(df_v2)
    # print(df_v2.info())
    df_v2.loc[(df_v2['Combustible'].isnull() | (df_v2['Combustible'] == '')), 'Combustible'] = 'GSL'
    Combustible.combus_number(df_v2)
    print(df_v2.shape)


    print('Applying simulation km')

    df_v2["Kilometraje"] = df_v2.apply(
        lambda row: mean_km_f(row["Modelo"], row["Fecha_venta"]) if pd.isna(row["Kilometraje"]) else row["Kilometraje"], 
        axis=1
    )
    print(df_v2.columns.tolist())
    df_v2 = generate_simulated_data(df_v2, 3)
    print(df_v2.shape)


    df_v2['Descripcion'] = '' 
    df_v2['Descripcion_int'] = 0

    print('Applying simulation damage score')
    df_v2 = simulate_damages(df_v2,3)
    print(df_v2.shape)

    df_v2['Blindaje'] = 0

    # df_v2 = TRM.apply_trm_logic(df_v2)
    dic_estado = {'Nuevos' : 0, 'Usados' : 1, 'Nuevo' : 0, 'Usado' : 1, ' ' : 1, 'Compras Usados' : 1}
    df_v2['Estado_vehiculo_int'] = df_v2['Estado_vehiculo'].map(dic_estado)
    df_v2 = df_v2.rename(columns={'Referencia' : 'Referencia_old'}) 
    df_v2 = df_v2.rename(columns={'Referencia2_fasecolda' : 'Referencia'})

    # df_v2['Popularidad'] = df_v2.apply(lambda row: Popularity.search_score(row['Cod_fasecolda'], row['Modelo']), axis=1)

    df_v2.head()
    df_v2['Pricing'] = df_v2.pop('Pricing')

    df_v2.drop(['Id_vehiculo', 'Placa', 'Vin', 'Compania', 'Marca_or', 'Linea_or', 'Cod_fasecolda_aprox', 'Proximidad_cod_fasecolda','Codigo'],
    axis='columns', inplace=True)


    df_v2.to_csv('../output_df_07_07_2025.csv', index=False)
    df_v2_h = df_v2.sort_values(['Kilometraje'], ascending=[False])
    df_v2_h = df_v2_h.head(100) 
    df_v2_h.to_excel('../output_v2.xlsx')

    df_2 = df_v2[df_v2['Kilometraje'] !=0.0]
    df_2.to_csv('../output_df_no0.csv', index=False)






    list_col = ['Cod_fasecolda', 'Marca', 'Linea', 'Referencia', 'Modelo', 'Kilometraje', 'Descripcion','Descripcion_int', 'Gama','Gama_int', 'Demanda', 'Popularidad', 'Combustible','Combustible_int', 'Estado_vehiculo', 'Estado_vehiculo_int', 'Fecha_venta', 'Year', 'Month','Blindaje', 'Ubicacion', 'Ubicacion_int', 'Precio']

    list_col = list(map(lambda x: x.lower(), list_col))

