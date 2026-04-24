import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import time
from datetime import datetime

from modelos_prueba.columns_check import columns_for_pricing
from CleaningData.app.cleaners.motos import Motos

path = r'../brdp_27_03_2026_clean.csv'

start = time.time()
df, df_cod = columns_for_pricing(path)

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

df['Precio_Maximo'] = df['Precio_DataCarro'].apply(lambda x: x*range_var(x)[0])
df['Precio_Minimo'] = df['Precio_DataCarro'].apply(lambda x: x*range_var(x)[1])
# df = df.drop_duplicates()

df['Cod_fasecolda'] = df_cod['Cod_fasecolda']
df['Placa'] = df_cod['Placa']
# df['Comments'] = np.nan
# df['Comments'] = df['Comments'].astype(str)
df = Motos.find_limitaciones(df)
df['Fecha_Precio_DataCarro'] = datetime.now().date()
df['Version_DataCarro'] = 'V_1.5.0.20_01_2026'

print(df.shape)


# y_pred = np.expm1(y_pred_log)

df.to_excel(r'C:\Users\manuel.torres\Modelos_Datacar\RF_brdp_27_03_2026_clean.xlsx')

end = time.time()

print(f"Execution time: {end - start:.2f} seconds")

