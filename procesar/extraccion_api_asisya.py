from procesar.sqlacces import connection_str_dw_fz
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import numpy as np
import os 
from pathlib import Path


def extraccion():
# Obtener la fecha actual
    fecha_hoy = datetime.now()
    fecha_formateada = fecha_hoy.strftime('%d_%m_%Y')
    # Imprimir la fecha en el formato dd_mm_yyyy


    connect_str: str = connection_str_dw_fz
    engine = create_engine(connect_str)
    query = f""" SELECT 
        A.*, 
        B.[Precio_DataCarro] AS Precio_brdp,
        B.[Fecha_Precio_DataCarro] AS Fecha_brdp,
        B.[Fecha_de_Inspeccion] as Fecha_inspec_brdp,
        C.[Precio_DataCarro] AS Precio_grc,
        C.[Fecha_Precio_DataCarro] AS fecha_grc,
        C.[Fecha_de_Inspeccion] as Fecha_inspec_grc
    FROM 
        [Analitica].[dbo].[peritajes_fasecolda] AS A 
    LEFT JOIN
        [Analitica].[pri].[pricing_brdp] AS B
    ON
        A.Placa = B.Placa

    LEFT JOIN 
        [Analitica].[pri].[pricing_grc] AS C 
    ON 
        A.Placa = C.Placa


    """

    query1 = "SELECT * FROM [Analitica].[dbo].[peritajes_fasecolda]"
    query2 = "SELECT Placa, [Precio_DataCarro] as Precio_brdp, [Fecha_de_Inspeccion] as Fecha_brdp FROM [Analitica].[pri].[pricing_brdp]"
    query3 = "SELECT Placa, [Precio_DataCarro] as Precio_grc, [Fecha_de_Inspeccion] as Fecha_grc FROM [Analitica].[pri].[pricing_grc]"

    # df = pd.read_sql(query, engine)
    df1 = pd.read_sql(query1, engine)
    df2 = pd.read_sql(query2, engine)
    df3 = pd.read_sql(query3, engine)


    engine.dispose()

    # DataFrame A (Peritajes)
    df1['Fecha'] = pd.to_datetime(df1['Fecha'], errors='coerce')
    df1['AnnoMes'] = (df1['Fecha'].dt.year * 10000) + \
                        (df1['Fecha'].dt.month * 100) + \
                        df1['Fecha'].dt.day
    df1['AnnoMes'] = df1['AnnoMes'].astype(int)

    df1['Placa'] = df1['Placa'].str.upper()
    df2['Placa'] = df2['Placa'].str.upper()
    df3['Placa'] = df3['Placa'].str.upper()

    # DataFrame B (Precios BRDP)
    df2['Fecha_brdp'] = pd.to_datetime(df2['Fecha_brdp'], errors='coerce')

    # df2['AnnoMes'] = df2['Fecha_brdp'].dt.year * 100 + df2['Fecha_brdp'].dt.month
    df2['AnnoMes'] = (df2['Fecha_brdp'].dt.year * 10000) + \
                        (df2['Fecha_brdp'].dt.month * 100) + \
                        df2['Fecha_brdp'].dt.day

    df2['AnnoMes'] = df2['AnnoMes'].fillna(0).astype(int)


    # DataFrame C (Precios GRC)
    df3['Fecha_grc'] = pd.to_datetime(df3['Fecha_grc'], errors='coerce')
    # df3['AnnoMes'] = df3['Fecha_grc'].dt.year * 100 + df3['Fecha_grc'].dt.month
    df3['AnnoMes'] = (df3['Fecha_grc'].dt.year * 10000) + \
                        (df3['Fecha_grc'].dt.month * 100) + \
                        df3['Fecha_grc'].dt.day
    df3['AnnoMes'] = df3['AnnoMes'].fillna(0).astype(int)

    df_m = pd.merge(df1, df2, how='left', on=['Placa','AnnoMes'])
    df_m2 = pd.merge(df_m, df3, how='left', on=['Placa','AnnoMes'])

    columnas_precio = ['Precio_brdp', 'Precio_grc']

    # 2. Reemplazar cadenas vacías ('') con NaN para unificar la búsqueda de NULL/Vacío
    # Usamos replace y inplace=True para modificar las columnas directamente.
    df_m2[columnas_precio] = df_m2[columnas_precio].replace('', np.nan)

    # 3. Aplicar la condición de filtro:
    #    (Precio_brdp es NaN) Y (Precio_grc es NaN)
    df_sin_precios = df_m2[
        df_m2['Precio_brdp'].isna() & 
        df_m2['Precio_grc'].isna()
    ].copy()

    df_sin_precios = df_sin_precios.rename(columns={'Marca_x' : 'Marca'})
    try:
        df_sin_precios['Motorización  / Tipo de Vehículo'] = df_sin_precios['Motorización  / Tipo de Vehículo'].replace('NO REPORTADO', 0)
    except:
        pass
    df_sin_precios.to_excel(f'brdp_{fecha_formateada}.xlsx', index=False)
    ruta_completa = Path(f'brdp_{fecha_formateada}.xlsx').resolve()
    print(f" Archivo guardado en: {ruta_completa}")
    # df4.to_excel(f'brdp_{fecha_formateada}.xlsx', index=False)

    df_m2.to_excel('revisar_todos.xlsx', index=False)
    ruta_completa =  Path('revisar_todos.xlsx').resolve()
    print(f" Archivo guardado en: {ruta_completa}")

    return df_sin_precios


if __name__ == '__main__':

    df = extraccion()

