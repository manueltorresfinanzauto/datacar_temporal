from CleaningData.app.general_clean import max_cleaner
import pandas as pd


def doble_ubi(df, ubicacion_doble):

    if ubicacion_doble:
        def remplace(text: str):
                replace_dict = {
                    "d.c.": "",
                    "el": "",
                    "la": "",
                    "de": "",
                    " ": ""
                }

                for old, new in replace_dict.items():
                    text = str(text).lower().replace(old, new)
                
                return text
        data = pd.read_excel("CleaningData/app/cleaners/MPIOS_MGN_2021_Names.xlsx",
                                  sheet_name="Sheet1")
        data['Muni_Nom_Cruce'] = (data['Muni_Nom_Cruce'].apply(remplace))

        def nivel_loc(location1, location2):
            location1_clean = remplace(location1)
            location2_clean = remplace(location2)
            loc1 = data.loc[data['Muni_Nom_Cruce'] == location1_clean.lower(), 'Nivel_Castigo'].values
            loc2 = data.loc[data['Muni_Nom_Cruce'] == location2_clean.lower(), 'Nivel_Castigo'].values
            # print(loc1, loc2)
            if len(loc1) == 0 or len(loc2) == 0:
                return 'Bogota D.C.'  # Handle missing values

            if loc1[0] > loc2[0]:
                return location1
            elif loc2[0] > loc1[0]:
                return location2
            else:
                return location1

        # Apply the function
        df_nuevo = df.copy
        df['ubicacion'] = df.apply(lambda row: nivel_loc(row['ubicacion2'], row['ubicacion3']), axis=1)
        # df.to_csv('input2.csv', index=False)
        # print(df.head(20))
        return df
    else:
        pass


def main():

    path_f = '/home/manueltorres/analitica-garaje/brdp_15_05.xlsx'
    df = pd.read_excel(path_f)
    if 'Valor alistamiento' in df.columns:
        df['Observaciones'] = df['Observaciones'] + ' ' + df['Valor alistamiento'].astype(str)
    Asousados = True
    if Asousados: 
        df = df.rename(columns={'REFERENCIA2_FASECOLDA' : 'Referencia'})


    ubicacion_doble = False
    if ubicacion_doble:
        df = doble_ubi(df, ubicacion_doble)
    
    df = max_cleaner(df)
    df.to_csv('../brdp_15_05_clean.csv', index=False)

def clean_total(path_f, name_out, df_o, ruta = True, Asousados = False, ubicacion_doble=False, save_csv=True):

    if ruta:
        df = pd.read_excel(path_f)
    else:
        df = df_o
        
    if 'Valor alistamiento' in df.columns:
        df['Observaciones'] = df['Observaciones'] + ' ' + df['Valor alistamiento'].astype(str)
    if Asousados: 
        df = df.rename(columns={'REFERENCIA1_FASECOLDA' : 'Linea', 'Referencia' : 'Referencia_old'})
        df = df.rename(columns={'REFERENCIA2_FASECOLDA' : 'Referencia'})
    if ubicacion_doble:
        df = doble_ubi(df, ubicacion_doble)
    df = max_cleaner(df)
    out_pa = f'../{name_out}'
    if save_csv:
        df.to_csv(out_pa, index=False)

    return df


if __name__=='__main__':

    main()