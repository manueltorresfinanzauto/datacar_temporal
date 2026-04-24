import pandas as pd 
import numpy as np


class Gamas:

    @staticmethod
    def call_df_gama():
        df_g = pd.read_excel('CleaningData/app/cleaners/Gamas.xlsx', sheet_name='Gamas 343')
        return df_g
    
    @classmethod
    def find_gamma(cls, df):
        df_g = cls.call_df_gama()
        df_g["Codigo"] = df_g["Codigo"].astype(int)
        df = df.merge(df_g[['Codigo', 'Criterio Percepción ']], left_on='Cod_fasecolda', right_on='Codigo', how='left')
        df = df.rename(columns={'Criterio Percepción ' : 'Gama'})
        dic_g = {'De Lujo ': 4, 'Gama Alta' : 3, 'Gama Media' : 2, 'Gama Baja' : 1}
        df['Gama_int'] = df['Gama'].map(dic_g)
        return df
    
    @staticmethod
    def safe_mode(series):
        mode_vals = series.mode()
        if not mode_vals.empty:
            return mode_vals.iloc[0]
        else:
            return np.nan  # o cualquier valor por defecto

    @classmethod
    def dic_gama(cls):
        df_g = cls.call_df_gama()

        dic_g = {'De Lujo ': 4, 'Gama Alta': 3, 'Gama Media': 2, 'Gama Baja': 1}
        reverse_dic_g = {v: k for k, v in dic_g.items()} 
        df_g['Gama_int'] = df_g['Criterio Percepción '].map(dic_g)
        # most_common = df_g.groupby('Marca')['Gamma_int'].agg(lambda x: x.mode()[0])
        most_common = df_g.groupby('Marca')['Gama_int'].agg(cls.safe_mode)
        dict_output = most_common.map(reverse_dic_g).to_dict()

        return dict_output

    @classmethod
    def add_gamma_mode(cls, df_2):
        
        dic_g = {'De Lujo ': 4, 'Gama Alta': 3, 'Gama Media': 2, 'Gama Baja': 1}

        dict_output = cls.dic_gama()
        dict_output  = {
                    k.lower().capitalize(): v
                    for k, v in dict_output.items()
                    }
        print(dict_output)
        # df_2['Gamma'] = df_2.apply(lambda row: dict_output[row['Marca']] if pd.isna(row['Gamma']) else row['Gamma'], axis=1)
        df_2['Gama'] = df_2.apply(lambda row: dict_output.get(row['Marca'], np.nan) if pd.isna(row['Gama']) else row['Gama'], axis=1)

        # Map Gamma to Gamma_int
        df_2['Gama_int'] = df_2['Gama'].map(dic_g)

        return df_2
    
    @classmethod
    
    def fill_nans_gammas(cls, df):
        dic_g = {'De Lujo ': 4, 'Gama Alta': 3, 'Gama Media': 2, 'Gama Baja': 1}

        df['Gama'] = df['Gama'].fillna('Gama Media')  
        df['Gama_int'] = df['Gama'].map(dic_g)

        return df



        