import pandas as pd 
import numpy as np 
import openpyxl
from app.cleaners.fasecol import tf_idf_assign
from datetime import datetime

def aso_f(camino):
    file_path = camino
    xls = pd.ExcelFile(file_path)

    # Get all sheet names
    sheet_names = xls.sheet_names
    print(sheet_names)
    print(len(sheet_names), 'numero de hojas')

    wb = openpyxl.load_workbook(file_path, data_only=True)
    df_final = pd.DataFrame()
    for i in range(1,len(sheet_names)):
    #     print(sheet_names[i])
    # for i in range(1,4):
        print(sheet_names[i])
        ws = wb[sheet_names[i]]

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_names[i],
            header=None,
            engine="openpyxl",
            keep_default_na=True,
            na_values=["", "#N/A", " ", 0]
        )

        columnas_correctas = ["SEGMENTO", "MARCA", "TIPO", "CATALOGO"]
        nombres_nuevos = df.iloc[1].fillna("").tolist()
        nuevos_nombres = columnas_correctas + nombres_nuevos[len(columnas_correctas):]
        df.columns = nuevos_nombres

        df = df.iloc[3:].reset_index(drop=True)
        df = df.loc[:, ~df.columns.astype(str).str.contains('%')]
        df.replace("", pd.NA, inplace=True)

        columnas_años = [col for col in df.columns if isinstance(col, (int, float))]
        columnas_2025 = [col for col in columnas_años if isinstance(col, (int, float)) and float(col) == 2025.0]
        if not columnas_2025:
            print(f"No se encontró la columna para el año 2025 en la hoja '{sheet_names[i]}'. Columnas disponibles: {columnas_años}")
            continue  # Puedes cambiar esto por raise si prefieres detener todo
        else:
            columna_nuevo = columnas_2025[0]
        columna_nuevo = columnas_2025[0]
        columnas_usado = columnas_años.copy()
        columnas_usado.remove(columna_nuevo)

        # Melt para autos nuevos
        df_nuevo = df.melt(
            id_vars=["MARCA", "CATALOGO"],
            value_vars=[columna_nuevo],
            var_name="Modelo",
            value_name="Precio"
        )
        df_nuevo["Estado"] = "Nuevo"

        # Melt para autos usados
        df_usado = df.melt(
            id_vars=["MARCA", "CATALOGO"],
            value_vars=columnas_usado,
            var_name="Modelo",
            value_name="Precio"
        )
        df_usado["Estado"] = "Usado"

        df_long = pd.concat([df_nuevo, df_usado], ignore_index=True)

        # Convertir precios
        df_long["Precio"] = pd.to_numeric(df_long["Precio"], errors="coerce")
        df_long["Precio"] = (df_long["Precio"] * 1e6).round(-5)
        #  eliminar las filas con nan or null en precio 
        df_long = df_long.dropna(subset=["Precio"])

        # Renombrar columnas
        df_long.rename(columns={"MARCA": "Marca", "CATALOGO": "Referencia"}, inplace=True)

        # --- ELIMINAR DUPLICADOS SOLO DE MODELO 2025 ---
        mask_2025 = df_long["Modelo"] == 2025
        df_long_2025 = df_long[mask_2025].drop_duplicates(subset=["Marca", "Referencia", "Modelo", "Estado"])
        df_long_otros = df_long[~mask_2025]

        df_long = pd.concat([df_long_2025, df_long_otros], ignore_index=True)

        
        

        df_final = pd.concat([df_final, df_long], ignore_index=True)
    
    df_final['Referencia'] = df_final['Referencia'].astype(str)
    df_final = tf_idf_assign.marca_cofc(df_final)
    df_final['Servicio'] = 'Particular'
    df_final.rename(columns={"Precio": "Pricing", 'Estado' : 'ESTADO_VENTA', 'Marca' : 'MARCA', 'Modelo' : 'ANIO_MODELO', 'cod_fasecolda':'COD_FASECOLDA'}, inplace=True)
    df_final[df_final['Pricing'] !=0]
    df_final.rename(columns={"Pricing": "PRECIO_VENTA"}, inplace=True)
    df_final['COMPANIA'] = 'Asousados'
    df_final['KILOMETRAJE'] = 0
    
    

    return df_final