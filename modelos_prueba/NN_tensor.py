import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf 
from tensorflow.keras import Sequential 
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization 
import seaborn as sns


from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils import resample

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import joblib
import time
import smogn



#  Clean the dataset
def clean_dataset(df):
    df_clean = df.copy()
    for col in df_clean.select_dtypes(include=[np.number]).columns:
        df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
        if df_clean[col].notnull().any():
            q_low = df_clean[col].quantile(0.001)
            q_high = df_clean[col].quantile(0.999)
            df_clean[col] = df_clean[col].clip(lower=q_low, upper=q_high)
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    return df_clean

#  Load and preprocess
file_path = '../../car_data.csv'
df = pd.read_csv(file_path)
df = clean_dataset(df)

selected_columns = ['Cod_fasecolda', 'Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Promedio_estrellas', 'Combustible', 'Descripcion_int', 'Gama', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Estado_vitrina','Pricing']
print(df.columns.tolist())

df = df[[col for col in selected_columns if col in df.columns]]

print(df.shape)

df['Estado_vitrina'] = (
    df['Estado_vitrina']
    .str.lower()          # Convierte a minúsculas
    .str.strip()          # Elimina espacios al inicio y final
    .str.replace(r'\s+', '_', regex=True)  # Reemplaza espacios internos por guiones bajos
)
reemplazos = {
    'venta_especial': 'venta_especial',
    'venta_especial_': 'venta_especial',
    'venta_especiales': 'venta_especial',
    'venta espcial' : 'venta_especial',
    'venta_espcial' : 'venta_especial'
    # Agrega más reemplazos según sea necesario
}

df['Estado_vitrina'] = df['Estado_vitrina'].replace(reemplazos)
# df = df.head(500)
# df = df.astype(float)
df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(str).str.zfill(8)
df['Marca_cod'] = df['Cod_fasecolda'].str[:3]
df['Tipolo_cod'] = df['Cod_fasecolda'].str[3:5]
df['Resto_cod'] = df['Cod_fasecolda'].str[5:]

df['Marca_cod'] = df['Marca_cod'].astype(int)
df['Tipolo_cod'] = df['Tipolo_cod'].astype(int)
df['Resto_cod'] = df['Resto_cod'].astype(int)
df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(int)

print(df.columns.tolist())

print(df.shape)
df['Modelo'] = df['Modelo'].replace('-', np.nan)
df = df.dropna(subset=['Modelo'])
df['Kilometraje'] = df['Kilometraje'].replace('-', 0)
df['Kilometraje'] = df['Kilometraje'].replace(r'[^\d.-]', '', regex=True)  # Elimina caracteres no numéricos

df['Kilometraje'] = pd.to_numeric(df['Kilometraje'], errors='coerce').fillna(0)  # Convierte a float
df['Pricing'] = pd.to_numeric(df['Pricing'], errors='coerce')
df = df.dropna(subset=['Pricing'])
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
# df.drop(columns=['Combustible', 'Gama', 'Estado_vitrina'], inplace=True)
df.drop(columns=['Gama_De Lujo ', 'Combustible_HBD', 'Vitrina_vitrina'], inplace=True)



X = df.drop(columns=['Pricing'])
y = df['Pricing']
y_log = np.log1p(y)
# y_log = y


## -------------- bootstraping ------------------------------------------------------------------------------
df_bootstrap = pd.concat([X, y_log], axis=1)

# Bootstrapping: generate a new dataset by sampling with replacement
df_bootstrap = resample(
    df_bootstrap,
    replace=True,
    n_samples=int(len(df_bootstrap) * 1.5),  # You can increase size; 1.5x is common
    random_state=42
)

# Separate the bootstrapped data
X = df_bootstrap.drop(columns=['Pricing'])
y_log = df_bootstrap['Pricing']
## ..........................................................................................................

print(df.shape)

# split the data

X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.3, random_state=42)
y_test_orig = np.expm1(y_test)
y_test_orig_log = y_test


def nn_model():
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=[len(X_train.keys())]))
    model.add(Dropout(0.2))
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())
    model.add(Dense(30, activation='relu'))
    model.add(Dense(1))

    return model 

model = nn_model()
print(model.summary())