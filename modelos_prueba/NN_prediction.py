import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf 
from tensorflow.keras import Sequential 
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization 
import seaborn as sns
from tensorflow.keras.models import load_model

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils import resample

import joblib
import time
# import smogn

def dum_col(df):
    if 'Vitrina_venta_especial' not in df.columns:
        df['Vitrina_venta_especial'] = 0 
        df['Vitrina_vitrina'] = 1
    if 'Combustible_DSL' not in df.columns:
        df['Combustible_DSL'] = 0
    if 'Combustible_ELT' not in df.columns:
        df['Combustible_ELT'] = 0 
    if 'Combustible_GAS' not in df.columns:
        df['Combustible_GAS'] = 0 
    if 'Combustible_GSL' not in df.columns:
        df['Combustible_GSL'] = 0
    if 'Combustible_HBD' not in  df.columns: 
        df['Combustible_HBD'] = 0
    if 'Gama_De Lujo ' not in df.columns:
        df['Gama_De Lujo '] = 0
    if 'Gama_Gama Alta' not in df.columns: 
        df['Gama_Gama Alta'] = 0
    if 'Gama_Gama Baja' not in df.columns:
        df['Gama_Gama Baja'] = 0 
    if 'Gama_Gama Media' not in df.columns:
        df['Gama_Gama Media'] = 0
    
    return df


df = pd.read_csv(r'C:\Users\manuel.torres\Modelos_Datacar\cientocincuenta_dat_marzo_2025_ex_result_clean.csv')

selected_columns = ['Cod_fasecolda', 'Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Promedio_estrellas', 'Combustible', 'Descripcion_int', 'Gama', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Estado_vitrina','Pricing']
# 
# print(df.columns.tolist())

df = df[[col for col in selected_columns if col in df.columns]]

print(df.shape)
# df = df.head(500)
# df = df.astype(float)
df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(str).str.zfill(8)
df['Marca_cod'] = df['Cod_fasecolda'].str[:3]
df['Tipolo_cod'] = df['Cod_fasecolda'].str[3:5]
df['Resto_cod'] = df['Cod_fasecolda'].str[5:]

df['Marca_cod'] = df['Marca_cod'].astype(int)
df['Tipolo_cod'] = df['Tipolo_cod'].astype(int)
df['Resto_cod'] = df['Resto_cod'].astype(int)
# print(df.columns.tolist())

print(df.shape)
df['Modelo'] = df['Modelo'].replace('-', np.nan)
df = df.dropna(subset=['Modelo'])
df['Kilometraje'] = df['Kilometraje'].replace('-', 0)
df['Kilometraje'] = df['Kilometraje'].replace(r'[^\d.-]', '', regex=True)  # Elimina caracteres no numéricos

df['Kilometraje'] = pd.to_numeric(df['Kilometraje'], errors='coerce').fillna(0)  # Convierte a float
# df['Pricing'] = pd.to_numeric(df['Pricing'], errors='coerce')
# df = df.dropna(subset=['Pricing'])
for i in selected_columns:
    if i == 'Combustible' or i == 'Gama' or i == 'Estado_vitrina':
        pass
    else:
        df[i] = df[i].astype(float)

df.drop(columns='Cod_fasecolda', inplace=True)
## ------------- categorical --------------------------------------------------------------------------
df = pd.get_dummies(df, columns=['Combustible'], prefix='Combustible')
df = pd.get_dummies(df, columns=['Gama'], prefix='Gama')
df = pd.get_dummies(df, columns=['Estado_vitrina'], prefix='Vitrina')
df = dum_col(df)
df['Ubicacion_int'] = df['Ubicacion_int'].fillna(0)
# print(df.columns.tolist())
# df.drop(columns=['Combustible', 'Gama', 'Estado_vitrina'], inplace=True)

df.drop(columns=['Gama_De Lujo ', 'Combustible_HBD', 'Vitrina_vitrina'], inplace=True)

selec_c = ['Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Descripcion_int', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Marca_cod', 'Tipolo_cod', 'Resto_cod', 'Combustible_DSL', 'Combustible_ELT', 'Combustible_GAS', 'Combustible_GSL', 'Gama_Gama Alta', 'Gama_Gama Baja', 'Gama_Gama Media', 'Vitrina_venta_especial']


df = df[[col for col in selec_c if col in df.columns]]
print(df.columns.tolist())

scaler = joblib.load('../../scaler_3.pkl')
df_sca = scaler.transform(df)

# df['Kilometraje'] = df['Kilometraje']/1e8
# df['Modelo'] = df['Modelo']/1e4
# df['Year'] = df['Year']/1e4
# df['Month'] = df['Month']/12
# df['Promedio_estrellas'] = df['Promedio_estrellas']/5
# df['Marca_cod'] = df['Marca_cod']/1000
# df['Tipolo_cod'] = df['Tipolo_cod']/100
# df['Resto_cod'] = df['Resto_cod']/1000


model = load_model('../../my_nn_model_pricing_3.keras')

prediction = model.predict(df_sca)


df['Pricing_NN'] = prediction
df['Pricing_NN'] = np.expm1(df['Pricing_NN']*50) 

# df = df.drop_duplicates()

# y_pred = np.expm1(y_pred_log)

df.to_excel(r'C:\Users\manuel.torres\Modelos_Datacar\NN_pred_cientocincuenta_dat_marzo_2025_ex_result_clean.xlsx')
