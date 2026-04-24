import pandas as pd
import numpy as np
import time 
from datetime import datetime


class score_simul():
    """
    This class is for the simulation of damages with the int score, where we are going to implement the punishment to the original price. 
    """


    def __init__(self, price : int):
        """ 
        Args: 
            price (int): Original price
        """
        self.price = price 
    
    def random_val(self, offset=0):
        # random value between 1 to 5
        seed = time.time_ns() % 100000 + offset
        np.random.seed(seed)
        numero_random : int = np.random.randint(1, 6)
        return numero_random    
    
    def percentage_val(self, damage_i : int):

        if damage_i == 0:
            return 0
        if damage_i == 1:
            return 1 - 0.05
        if damage_i == 2:
            return 1 - 0.07
        if damage_i == 3:
            return 1 - 0.3 
        if damage_i == 4:
            return 1 - 0.13
        if damage_i == 5:
            return 1 - 0.5
        
    def final_price(self, damage_i : int):
        """
        Calculate the price of the vehicle based on the given price and percentage.

        Args:
            self

        Returns:
            float: The calculated price.
        """
        new_price : float = self.price * self.percentage_val(damage_i)
        return round(new_price) 
    
def simulate_damages(df, num_new_rows=3) -> pd.DataFrame:
    """
    Generates simulated data by applying a transformation based on specific columns.
    
    Args:
        df (pd.DataFrame): Input DataFrame with N columns.
        num_new_rows (int): Number of new rows to generate per existing row.
        
    Returns:
        pd.DataFrame: Original DataFrame concatenated with the simulated data.
    """
    new_rows = []
    if 'Descripcion_int' not in df.columns:
        df['Descripcion_int'] = 0 
    # Ensure required columns exist
    required_cols = {"Descripcion_int","Pricing"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"The DataFrame must contain the columns: {required_cols}")
    
    # Identify other columns to keep (excluding Kilometraje, Modelo, Pricing)
    other_cols = [col for col in df.columns if col not in required_cols]

    for _, row in df.iterrows():
        descrip_orig, pr_orig = row["Descripcion_int"], row["Pricing"]
        other_values = [row[col] for col in other_cols]  # Extract other column values

        if descrip_orig == 0: 
            for i in range(num_new_rows):
                simulation_obj_dam = score_simul(pr_orig)
                new_score_dam = int(simulation_obj_dam.random_val())
                price_new_dam = simulation_obj_dam.final_price(new_score_dam)

                new_rows.append(other_values + [new_score_dam, price_new_dam])
    df_new = pd.DataFrame(new_rows, columns= other_cols + ["Descripcion_int","Pricing"])
    return pd.concat([df, df_new], ignore_index=True)


if __name__ == '__main__':

    # To test the code 
    data = [['fase1', 'day1', 2020, 15e3, 500], ['fase2', 'day2', 2022,15e3*2, 300]]
    df = pd.DataFrame(data, columns=['F', 'D', 'Modelo', 'Kilometraje', 'Pricing'])
    df_simulated = simulate_damages(df, num_new_rows=3)
    print(df_simulated.head(12))
    print(df_simulated.shape)









