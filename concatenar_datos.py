import pandas as pd 
from datetime import datetime

df_1_str : str = '../car_data_V_1_5_2025_10_07.csv'
df_2_str : str = '../output_df_07_01_2026_clean.csv' 
df_3_str : str = '../check__porcentajes_correccion_clean.csv' 
df_4_str : str = '../melollevo_2025_facturas_faltantes_clean.csv' 
# df_5_str : str = '../aso_agosto_2024_clean_clean.csv' 
# df_6_str : str = '../aso_enero_2024_clean_clean.csv' 
# df_7_str : str = '../aso_diciembre_2023_clean_clean.csv' 
# df_8_str : str = '../aso_abril_2024_clean_clean.csv' 
# df_9_str : str = '../aso_junio_2025_clean_clean.csv' 
# df_10_str : str = '../aso_marzo_2025_clean_clean.csv' 
# df_11_str : str = '../aso_abril_2024_clean_clean.csv' 

df1 = pd.read_csv(df_1_str)
df2 = pd.read_csv(df_2_str)
df3 = pd.read_csv(df_3_str)
df4 = pd.read_csv(df_4_str)
# df5 = pd.read_csv(df_5_str)
# df6 = pd.read_csv(df_6_str)
# df7 = pd.read_csv(df_7_str)
# df8 = pd.read_csv(df_8_str)
# df9 = pd.read_csv(df_9_str)
# df10 = pd.read_csv(df_10_str)
# df111 = pd.read_csv(df_11_str)

dic_estado = {'Nuevos' : 0, 'Usados' : 1, 'Nuevo' : 0, 'Usado' : 1}
# df5['Estado_vehiculo_int'] = df5['Estado_vehiculo'].map(dic_estado)
df2 = df2.drop(columns=['Ubicacion_int.1'])
print(df1.shape)
df_final = pd.concat([df1,  df3, df4], ignore_index=True)

df_final['Estado_vitrina_int'] = df_final['Estado_vitrina_int'].fillna(0)
df_final['Ubicacion_int'] = df_final['Ubicacion_int'].fillna(0)
df_final['Kilometraje'] = df_final['Kilometraje'].astype(str).str.replace('.','',regex=False).str.replace(' ','', regex=False).str.replace(',','', regex=False)
df_final = df_final[~df_final['Kilometraje'].isin(['-', 'Sin Inf', 'SinInf'])]
df_final['Kilometraje'] = df_final['Kilometraje'].astype(float)
df_final['Kilometraje'] = df_final['Kilometraje'].clip(lower=0)

hoy = str(datetime.today().strftime('%Y_%m_%d'))
df_final = df_final.dropna(subset=['Cod_fasecolda'])

name_version = 'car_data_V_1_5_'+hoy+'.csv'
print(name_version)
print(df_final.shape)

print(df_final.columns)

df_final = df_final.drop(columns=['Unnamed: 0.5', 'Unnamed: 0.4', 'Unnamed: 0.3', 'Unnamed: 0.2',
       'Unnamed: 0.1', 'Unnamed: 0', 'Descripcion', 'Placa'])

df_final.to_csv(f'../{name_version}')