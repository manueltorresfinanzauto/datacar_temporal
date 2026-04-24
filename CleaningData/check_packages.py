# Personal 
from app.cleaners.punishment_damage import VehicleDamage  
from app.Simul.simulate import Simulation_p_k 
import pandas as pd 
from tqdm import tqdm
from app.cleaners.search_code_faseco import Fasecol 
from app.cleaners.demand import Demanda
from app.cleaners.popula import Popularity
from app.cleaners.combus import Combustible
from app.cleaners.fasecol import tf_idf_assign
from app.cleaners.marcalinea import MarcaLinea

tqdm.pandas(desc="Processing")


# test = VehicleDamage()
# output = test.level_extraction_llm('Vehiculo en mal estado general, con focos de contaminacion (vehiculo trasladado de la costa),AC no funciona posible daño en compresosr$1.200.000,Golpe leve trasero,cambio de 2 llantas$700.000, rin de lujo+llanta$700.000,sincronizacion$600.000,revisar suspencion$600.000,5 piezas de pintura y latoneria $$1.500.000,cambio de correa de accesorios $180.000,Stop roto $350.000,aceite $400.000,bateria$400.000')
# output = ({'respuesta': {'nivel': 3}}, 3)
# print(output['respuesta']['nivel'], type(output['respuesta']['nivel'],))
# print(output)

# call1 = Popularity.search_score(3006125, 2015)
# print(call1)

# call2 = Combustible.search_combus(3006125)
# print(call2)

# call_fase = Fasecol.search_score('MAZDA', '3', 'Z6HM5')
# print(call_fase)

# df = pd.read_excel('Listado_para_Pricing_25_de_Febrero_2025.xlsx', index_col=0)
# print(df.head())
# df['reference'] = df['reference'].apply(tf_idf_assign.cleaning_text)
# print(df.head())
# df['reference'] = df['reference'].apply(tf_idf_assign.remove_duplicate_words)

# df_n = tf_idf_assign.assign_cofc(df)
# print(df_n.head())
# print(df_n.info())
# header = ['Marca', 'reference', 'cod fasecolda', 'marca', 'referencia', 'referencia2', 'referencia3',  'jaccard']
# df.to_csv('out.csv', columns = header, index=False)

# import pandas as pd
# import numpy as np

# # Example of the first DataFrame
# df1 = pd.DataFrame({'code': [101, 102, 103, 200, np.nan],
#                     'hola1': ['a', 'b', 'c', 'e', 'f']})

# # Example of the second DataFrame
# df2 = pd.DataFrame({
#     'cod_fase': [101, 102, 103, 104],
#     'col1': ['A', 'B', 'C', 'D'],
#     'col2': [10, 20, 30, 40],
#     'col3': [0.1, 0.2, 0.3, 0.4]
# })


# # Merge the DataFrames
# df_merged = df1.merge(df2, left_on='code', right_on='cod_fase', how='left').drop(columns=['cod_fase'])

# print(df_merged)

# -----------------------------------------------------------------------------------------------------------
# ya pensando en el df final 
# -----------------------------------------------------------------------------------------------------------


# df['Year'] = df['datetime'].dt.year
# df['Month'] = df['datetime'].dt.month
# df['day'] = df['datetime'].dt.day 

list_col = ['cod_fasecolda', 'Marca', 'Linea', 'Referencia', 'Modelo', 'Kilometraje', 'Descripcion','Descripcion_int', 'Gama','Gama_int', 'Demanda', 'Popularidad', 'Combustible','Combustible_int', 'Estado_vehiculo', 'Estado_vehiculo_int', 'Fecha_venta', 'Year', 'Month','Blindaje', 'Ubicacion', 'Ubicacion_int', 'Precio']

# df_new = df_old[list_col].copy()


# print(Demanda.search_demanda(2019, 'Renault', 'kwid', 2020))

# rstring : str = '../Listado_para_Pricing_25_de_Febrero_2025.xlsx'
# df = pd.read_excel(rstring)
# df['Observaciones_numero'] = df['Observaciones'].progress_apply(lambda x: test.level_extraction_llm(x))
# print(df.head())
