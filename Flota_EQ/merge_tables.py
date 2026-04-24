import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from CleaningData.config.sqlacces import connection_str, connection_str_dw_fz


# SQL --------------------------------------------------------------------------------------------------------

def querys(x : int, y : str = None):
    if x == 0:
        query = """   select distinct [Version_GFC] FROM [Analitica].[dbo].[COD_Fasecolda] order by Version_GFC desc;
            """
        
    if x == 1:
        query  = f""" 
    SELECT  [Marca]
      ,[Clase]
      ,[Codigo]
      ,[Homologocodigo]
      ,[Referencia1]
      ,[Referencia2]
      ,[Referencia3]
      ,[Peso]
      ,[IdServicio]
      ,[Servicio]
      ,[1970]
      ,[1971]
      ,[1972]
      ,[1973]
      ,[1974]
      ,[1975]
      ,[1976]
      ,[1977]
      ,[1978]
      ,[1979]
      ,[1980]
      ,[1981]
      ,[1982]
      ,[1983]
      ,[1984]
      ,[1985]
      ,[1986]
      ,[1987]
      ,[1988]
      ,[1989]
      ,[1990]
      ,[1991]
      ,[1992]
      ,[1993]
      ,[1994]
      ,[1995]
      ,[1996]
      ,[1997]
      ,[1998]
      ,[1999]
      ,[2000]
      ,[2001]
      ,[2002]
      ,[2003]
      ,[2004]
      ,[2005]
      ,[2006]
      ,[2007]
      ,[2008]
      ,[2009]
      ,[2010]
      ,[2011]
      ,[2012]
      ,[2013]
      ,[2014]
      ,[2015]
      ,[2016]
      ,[2017]
      ,[2018]
      ,[2019]
      ,[2020]
      ,[2021]
      ,[2022]
      ,[2023]
      ,[2024]
      ,[2025]
      ,[Version_GFC]
      ,[2026]
  FROM [Analitica].[dbo].[COD_Fasecolda]
  where [Version_GFC] = '{y}';    
"""

    return query

connect_str: str = connection_str_dw_fz
engine = create_engine(connect_str)
query = querys(0)
df_cod1 = pd.read_sql(query, engine)
first_value = df_cod1.iloc[0, 0]
query = querys(1, first_value)
df_cod2 = pd.read_sql(query, engine)
engine.dispose()

def lookup_value(row):
    id_code = row['Código Fasecolda']
    year = row['Modelo']
    # Find the matching row in df_2
    matched_row = df_cod2[df_cod2['Codigo'] == id_code]
    if not matched_row.empty and str(year) in matched_row.columns:
        return matched_row.iloc[0][str(year)]
    else:
        return None




ruta_eq = r'C:\Users\manuel.torres\Modelos_Datacar\EQ_tablas'

tab1 = '202505-flota-eq-fz.xlsx'
tab2 = 'c3b1ddc0-11de-4920-ae14-3ed4c39ea6cf.xls'
tab3 = 'NIIF.xls'

p_tab1 = os.path.join(ruta_eq, tab1)
p_tab2 = os.path.join(ruta_eq, tab2)
p_tab3 = os.path.join(ruta_eq, tab3)


df_1 = pd.read_excel(p_tab1)
tables2 = pd.read_html(p_tab2)  # Esto devuelve una lista de tablas encontradas
df_2 = tables2[0] 
tables3 = pd.read_html(p_tab3)  # Esto devuelve una lista de tablas encontradas
df_3 = tables3[0] 

# print(df_1.columns)
# print(df_2.columns)
# print(df_3.columns)

df_2['Ciudad_trabajo'] = df_2['Dim Geogrefica'].str.extract(r'^[^-]+-[^-]+-([^-]+)-')

df_merge1 = pd.merge(df_1,df_2[['Placa', 'Ciudad_trabajo']], how='left', on='Placa')

df_3 = df_3[df_3['Tipo'] == 'Vehiculo']

df_merge = pd.merge(df_merge1, df_3[['vehn_id', 'Libros contables', 'Asousados']], how='left', left_on='Vehn_id', right_on='vehn_id')


df_merge = df_merge.rename(columns={'Libros contables' : 'Valor NIIF'})

df_merge['Valor fasecolda'] = df_merge.apply(lookup_value, axis=1)
df_merge['Valor fasecolda'] = df_merge['Valor fasecolda']*1000
df_merge['Guia fasecolda'] = first_value
df_merge['Valor fiscal'] = np.nan
df_merge['Valor comite expertos'] = np.nan

print(df_merge.columns)
print(df_merge.head(5))

df_merge.to_excel('flota_eq_2025_06.xlsx', index=False)


# print(df_1)