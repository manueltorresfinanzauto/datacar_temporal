import joblib
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns




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


def columns_model(file_path):
    
    df = pd.read_csv(file_path)
    df['Pricing'] = df['Pricing'].astype(float)
    df = df[df['Pricing'] > 0.0]
    df = clean_dataset(df)


    selected_columns = ['Cod_fasecolda', 'Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Promedio_estrellas', 'Combustible', 'Descripcion_int', 'Gama', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Estado_vitrina','Pricing']
    print(df.columns.tolist())

    df = df[[col for col in selected_columns if col in df.columns]]
    df['Combustible'] = df['Combustible'].replace({'HEV':'HBD', 'MHEV':'HBD', 'PHEV':'HBD' })
    print(df.shape)
    df = df.dropna(subset=['Pricing'])
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
    print('columns list: ')
    print(df.columns.tolist())
    df.drop(columns=['Gama_De Lujo ', 'Combustible_HBD', 'Vitrina_vitrina'], inplace=True)
    print(df.columns.tolist())
    df = df.drop('Promedio_estrellas', axis=1)

    return df


def columns_for_pricing(file_path, df_o = None, ruta = True):

    if ruta:
        df = pd.read_csv(file_path)
    else: 
        df = df_o
    df_temp = df[['Cod_fasecolda', 'Placa']].copy()
    def dum_col(df):
        if 'Vitrina_venta_especial' not in df.columns:
            df['Vitrina_venta_especial'] = 0 
            df['Vitrina_vitrina'] = 1
        if 'Combustible_DSL' not in df.columns:
            df['Combustible_DSL'] = False
        if 'Combustible_ELT' not in df.columns:
            df['Combustible_ELT'] = False 
        if 'Combustible_GAS' not in df.columns:
            df['Combustible_GAS'] = False 
        if 'Combustible_GSL' not in df.columns:
            df['Combustible_GSL'] = False
        if 'Combustible_HBD' not in  df.columns: 
            df['Combustible_HBD'] = False
        if 'Gama_De Lujo ' not in df.columns:
            df['Gama_De Lujo '] = False
        if 'Gama_Gama Alta' not in df.columns: 
            df['Gama_Gama Alta'] = False
        if 'Gama_Gama Baja' not in df.columns:
            df['Gama_Gama Baja'] = False 
        if 'Gama_Gama Media' not in df.columns:
            df['Gama_Gama Media'] = False
        
        return df



    print(df.shape)

    selected_columns = ['Cod_fasecolda', 'Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda',  'Combustible', 'Descripcion_int', 'Gama', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Estado_vitrina']
    print(df.columns.tolist())

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
    df['Ubicacion_int'] = df['Ubicacion_int'].fillna(0)
    print(df.columns.tolist())

    print(df.shape)
    df['Modelo'] = df['Modelo'].replace('-', np.nan)
    df['Modelo'] = df['Modelo'].fillna(2020)
    # df = df.dropna(subset=['Modelo'])
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
    print(df.columns.tolist())
    # df.drop(columns=['Combustible', 'Gama', 'Estado_vitrina'], inplace=True)

    df.drop(columns=['Gama_De Lujo ', 'Combustible_HBD', 'Vitrina_vitrina'], inplace=True)

    selec_c = ['Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Descripcion_int', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Marca_cod', 'Tipolo_cod', 'Resto_cod', 'Combustible_DSL', 'Combustible_ELT', 'Combustible_GAS', 'Combustible_GSL', 'Gama_Gama Alta', 'Gama_Gama Baja', 'Gama_Gama Media', 'Vitrina_venta_especial']

    df = df[[col for col in selec_c if col in df.columns]]
    print(df.columns.tolist())
    print(df.shape)

    return df, df_temp

#  Load and preprocess


# file_path = '../../car_data_v1_3.csv'
# df = pd.read_csv(file_path)
# df = clean_dataset(df)

# selected_columns = ['Cod_fasecolda', 'Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Promedio_estrellas', 'Combustible', 'Descripcion_int', 'Gama', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Estado_vitrina','Pricing']
# print(df.columns.tolist())

# df = df[[col for col in selected_columns if col in df.columns]]

# print(df.shape)

# df['Estado_vitrina'] = (
#     df['Estado_vitrina']
#     .str.lower()          # Convierte a minúsculas
#     .str.strip()          # Elimina espacios al inicio y final
#     .str.replace(r'\s+', '_', regex=True)  # Reemplaza espacios internos por guiones bajos
# )
# reemplazos = {
#     'venta_especial': 'venta_especial',
#     'venta_especial_': 'venta_especial',
#     'venta_especiales': 'venta_especial',
#     'venta espcial' : 'venta_especial',
#     'venta_espcial' : 'venta_especial'
#     # Agrega más reemplazos según sea necesario
# }

# df['Estado_vitrina'] = df['Estado_vitrina'].replace(reemplazos)
# # df = df.head(500)
# # df = df.astype(float)
# df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(str).str.zfill(8)
# df['Marca_cod'] = df['Cod_fasecolda'].str[:3]
# df['Tipolo_cod'] = df['Cod_fasecolda'].str[3:5]
# df['Resto_cod'] = df['Cod_fasecolda'].str[5:]

# df['Marca_cod'] = df['Marca_cod'].astype(int)
# df['Tipolo_cod'] = df['Tipolo_cod'].astype(int)
# df['Resto_cod'] = df['Resto_cod'].astype(int)
# df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(int)

# print(df.columns.tolist())

# print(df.shape)
# df['Modelo'] = df['Modelo'].replace('-', np.nan)
# df = df.dropna(subset=['Modelo'])
# df['Kilometraje'] = df['Kilometraje'].replace('-', 0)
# df['Kilometraje'] = df['Kilometraje'].replace(r'[^\d.-]', '', regex=True)  # Elimina caracteres no numéricos

# df['Kilometraje'] = pd.to_numeric(df['Kilometraje'], errors='coerce').fillna(0)  # Convierte a float
# df['Pricing'] = pd.to_numeric(df['Pricing'], errors='coerce')
# df = df.dropna(subset=['Pricing'])
# for i in selected_columns:
#     if i == 'Combustible' or i == 'Gama' or i == 'Estado_vitrina':
#         pass
#     else:
#         df[i] = df[i].astype(float)

# df.drop(columns='Cod_fasecolda', inplace=True)
# ## ------------- categorical --------------------------------------------------------------------------
# df = pd.get_dummies(df, columns=['Combustible'], prefix='Combustible')
# df = pd.get_dummies(df, columns=['Gama'], prefix='Gama')
# df = pd.get_dummies(df, columns=['Estado_vitrina'], prefix='Vitrina')
# # df.drop(columns=['Combustible', 'Gama', 'Estado_vitrina'], inplace=True)
# print('columns list: ')
# print(df.columns.tolist())
# df.drop(columns=['Gama_De Lujo ', 'Combustible_HBD', 'Vitrina_vitrina'], inplace=True)
# print(df.columns.tolist())