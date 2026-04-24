import pandas as pd 
import numpy as np
from app.cleaners.location import Location
from app.asousados.reorganizar import aso_f 
from datetime import datetime



def main():

    # aso_f()
    import pandas as pd

    # Example DataFrame
    data = {
        'A': [1, 2, 3, 4, 5],
        'B': ['Nuevo', 'Usado', 'Nuevo', 'Antiguo', 'Nuevo'],
        'C': [10, 20, 30, 40, 50]
    }

    df = pd.DataFrame(data)

    # Filter where column B == "Nuevo"
    df_filtered = df[df['B'] == 'Nuevo']

    # print(df_filtered)
    str_path = '/home/manueltorres/analitica-garaje/AsoUsados_Abril.xlsx'
    df_final = aso_f(str_path)
    fecha_dt = datetime(2025, 11, 7)
    df_final['FECHA_VENTA'] = fecha_dt
    df_final.to_csv('../AsoUsados_Abril_clean.csv', index=False)
    df_final.to_excel('../AsoUsados_Abril_clean.xlsx')
    

if __name__ == '__main__':

    main()


