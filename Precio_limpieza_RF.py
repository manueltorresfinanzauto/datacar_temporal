import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import time
from datetime import datetime
from modelos_prueba.columns_check import columns_for_pricing
from CleaningData.app.cleaners.motos import Motos
from CleaningData.clean_main import clean_total 
import platform


start = time.time()

limpieza = True 

path = r'../brdp_23_04_2026.xlsx'

if limpieza:
    so = platform.system()
    if so == 'Windows':
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('Esta parte del código sirve en en WSL o Linux para obtener el puntaje de daños, si se corre en Windows el puntaje de daños va a ser 0. Tener muy en cuenta el sistema operativo')
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    # El path toca cambiarlo 
    
    name_out = 'Vehiculosclean.csv'
    df_or = clean_total(path, name_out, ubicacion_doble=False, save_csv=False)
    


path = r'../' + name_out
df, df_cod = columns_for_pricing(path, df_or,False)

# path to the pkl file that has the trained RF, it is the output file from the python Training_RF.py
model = joblib.load(r'C:\Users\manuel.torres\Modelos_Datacar\RF_model_V1_20_01_2026.pkl')


predicciones = model.predict(df)

df['Precio_DataCarro'] = predicciones 
df['Precio_DataCarro'] = np.expm1(df['Precio_DataCarro']) 
# df['Precio_DataCarro'] = df['Precio_DataCarro']

df['Precio_DataCarro'] = np.round(df['Precio_DataCarro'] / 100000) * 100000

def range_var(x):
    if x < 1e8:
        per = 0.05 
    elif x < 1.5e8: 
        per = 0.04
    elif x < 2e8:
        per = 0.03
    else: 
        per = 0.02 
    positivo = 1 + per 
    negativo = 1 - per

    return positivo, negativo

def range_var(x):
    if x < 1e8:
        per = 0.05 
    elif x < 1.5e8: 
        per = 0.04
    elif x < 2e8:
        per = 0.03
    else: 
        per = 0.02 
    positivo = 1 + per 
    negativo = 1 - per

    return positivo, negativo

df['Precio_Maximo'] = df['Precio_DataCarro'].apply(lambda x: x*range_var(x)[0])
df['Precio_Minimo'] = df['Precio_DataCarro'].apply(lambda x: x*range_var(x)[1])
# df = df.drop_duplicates()

df['Cod_fasecolda'] = df_cod['Cod_fasecolda']
df['Placa'] = df_cod['Placa']

df = Motos.find_limitaciones(df)
df['Fecha_Precio_DataCarro'] = datetime.now().date()
df['Version_DataCarro'] = 'V_1.5.0.07-10-2025'
print(df.shape)

df.to_excel(r'C:\Users\manuel.torres\Modelos_Datacar\RF_brdp_23_04_2026.xlsx')

end = time.time()

print(f"Execution time: {end - start:.2f} seconds")

