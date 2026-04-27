import pandas as pd
from Precio_limpieza_RF import main_datacarro
from procesar.extraccion_api_asisya import extraccion
from procesar.estandar_y_sql import main_estandar
from datetime import datetime


def pipe(brdp: bool=True, ruta_file: str = None):
    if brdp:
        fecha_hoy = datetime.now()
        fecha_formateada = fecha_hoy.strftime('%d_%m_%Y')
        nombre = f'brdp_{fecha_formateada}'
        df_perito = extraccion()
        df1 = main_datacarro(nombre, df_o=df_perito, ruta=False)
        main_estandar(df1)
        print(df1.head())
        # print(nombre)
    else:

        df1 = main_datacarro(ruta_file, df_o=None, ruta=True)


if __name__ == '__main__':
    # pipe()
    pipe(brdp=False, ruta_file='libro1.xlsx')
