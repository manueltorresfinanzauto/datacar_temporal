import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import time
from datetime import datetime
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from modelos_prueba.columns_check import columns_for_pricing
from CleaningData.app.cleaners.motos import Motos
from tensorflow.keras.models import load_model


path = r'../brdp_21_01_2026_clean.csv'

start = time.time()
df, df_cod = columns_for_pricing(path)

# path to the pkl file that has the trained RF, it is the output file from the python Training_RF.py
scaler = joblib.load('../scaler_20260121.pkl')
model = load_model('../my_nn_model_pricing_20260121.keras')
label_encoders = joblib.load('../label_encoders_20260121.pkl') # You need this!

# 2. Define the column groups exactly as training
categorical_cols = ['Combustible_DSL', 'Combustible_ELT', 'Combustible_GAS', 
                    'Combustible_GSL', 'Gama_Gama Alta', 'Gama_Gama Baja', 
                    'Gama_Gama Media', 'Vitrina_venta_especial', 'Ubicacion_int', 
                    'Descripcion_int', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int']
numeric_cols = [col for col in df.columns if col not in categorical_cols + ['Pricing']]

# 3. Process Categorical Columns (Label Encoding)
X_cat_inference = []
for col in categorical_cols:
    le = label_encoders[col]
    # Handle unseen labels by converting to string and transforming
    df[col] = le.transform(df[col].astype(str))
    X_cat_inference.append(df[col].values)

# 4. Process Numerical Columns (Scaling)
# ONLY transform the numeric columns
X_num_inference = scaler.transform(df[numeric_cols])

# 5. Reconstruct the list format for Keras
# This matches: [cat1, cat2, ..., catN, numeric_matrix]
X_inference = [np.array(col) for col in X_cat_inference] + [X_num_inference]

# 6. Predict and Inverse Transform Target
predicciones = model.predict(X_inference)

# predicciones = model.predict(df)

# predicciones = model.predict(df)

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
df['Version_DataCarro'] = 'V_NN_1'

print(df.shape)


# y_pred = np.expm1(y_pred_log)

df.to_excel(r'C:\Users\manuel.torres\Modelos_Datacar\NN_brdp_21_01_2026_clean.xlsx')

end = time.time()

print(f"Execution time: {end - start:.2f} seconds")

