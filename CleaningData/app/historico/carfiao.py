import pandas as pd 
import numpy as np 
import openpyxl
from app.cleaners.fasecol import tf_idf_assign
import re
from unidecode import unidecode

def clean_text(text, replace_dict=None):
    """
    Limpia el texto con los siguientes pasos:
    - Convierte a string
    - Convierte a minúsculas
    - Elimina tildes
    - Reemplaza según un diccionario (si se provee)
    - Elimina puntuaciones, caracteres especiales y múltiples espacios
    """

    # Asegurar que es string
    text = str(text)

    # Convertir a minúsculas y eliminar tildes
    text = unidecode(text.lower())

    # Reemplazos personalizados si hay diccionario
    if replace_dict:
        for old, new in replace_dict.items():
            text = text.replace(old, new)

    # Limpieza general
    text = re.sub(r"[.,]", "", text)             # Quitar puntos y comas
    text = re.sub(r"\s+", " ", text)             # Espacios múltiples por uno solo
    text = re.sub(r"[^\w\s]", "", text)          # Eliminar caracteres especiales
    text = re.sub(r"\[.*?\]", "", text)          # Eliminar contenido entre corchetes
    text = text.strip()                          # Quitar espacios al inicio/fin

    return text

dic_col = {'Tipo de servicio':'Servicio', 'Transito' : 'Ubicacion', 'Codigo fasecolda' : 'Cod_fasecolda', 'Precio' : 'Pricing', 'Fecha de pricing': 'Fecha pricing', 'Fecha del pricing': 'Fecha pricing', 'Lugar de matricula' : 'Ubicacion', 'Fasecolda' : 'Cod_fasecolda', 'Faseco' : 'Cod_fasecolda', 'Cod fasecolda':'Cod_fasecolda', 'Observacion':'Observaciones', 'Dias en finanzauto':'Dias en fz'}

def his_carfi():

    
    file_path = 'list_ex.txt'

    # df_final = pd.DataFrame()
    df_final = None
        
    with open(file_path, 'r') as in_file:
        lines = in_file.readlines()

    # Limpiar cada línea quitando espacios en blanco y saltos de línea
    lines = [line.strip() for line in lines]

    # Imprimir resultado limpio
    # print(lines)
    for archivos in lines:
        print(archivos)
        df = pd.read_excel(archivos)
        df.columns = [clean_text(col).capitalize() for col in df.columns]
        df = df.rename(columns=dic_col)
        # Normaliza nombres de columnas por si acaso (elimina espacios)
        df.columns = df.columns.str.strip()
        # print(df.columns)
        # Verifica ignorando mayúsculas/minúsculas
        if not any(col.lower() == "cod_fasecolda" for col in df.columns):
            df = tf_idf_assign.marca_cofc(df)
            df = df.rename(columns={'cod_fasecolda':'Cod_fasecolda'})


        # print(df)
        # df_final = df_final.reset_index()
        # df = df.reset_index()
        print(f'Shape df {df.shape}')
        if df_final is None:
            df_final = df
        else:
            try:
                df_final = pd.concat([df_final, df], ignore_index=True, sort=False)
            except:
                print(df.columns.tolist())
                print(df_final.columns.tolist())
                break
        print(f'Shape _final {df_final.shape}')

    l2 = ['Placa', 'Marca', 'Linea', 'Modelo', 'Cod_fasecolda', 'Estado','Kilometraje', 'Ubicacion', 'Servicio', 'Observaciones', 'Pricing', 'Fecha pricing', 'Dias en fz']

    # Obtener el resto de columnas que no están en l2
    otras_columnas = [col for col in df_final.columns if col not in l2]

    # Reordenar
    df_final = df_final[l2 + otras_columnas]
    df_final.drop(['O', 'Fg'], axis='columns', inplace=True)

    df_final.loc[df_final['Servicio'] == 'PARTICULAR', 'Servicio'] = 'Particular'
    df_final.loc[df_final['Servicio'] == 'público', 'Servicio'] = 'Publico'
    df_final = df_final[df_final['Pricing'] != 0.0]
    df_final['Servicio'] = df_final['Servicio'].fillna('Particular')
    # df_final['Estado'] = df_final['Estado'].fillna('Particular')





    df_final.to_csv('historico_carfiao.csv', index=False)
    df_final.to_excel('historico_carfiao.xlsx', index=False)

    return df_final