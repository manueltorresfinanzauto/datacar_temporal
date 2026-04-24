import pandas as pd
import numpy as np
import time 
from datetime import datetime

class Simulation_p_k():
    """
    This class is to simulate the kilometers and the punishment to the original price, we are taking into account that the average km of a particular car per year is 15000 km.  
    """

    MEAN_KM : int = 15000
    KM_THRESHOLD: float = 0.85 
    MAX_PENALTY: float = 0.45
    def __init__(self, price: int, model: int, km: int):
        """ 
        Args: 
            price (int): Original price
            model (int): The model year of the vehicle 
            km (int) : The km of the vehicle
        """
        self.price = price 
        self.model = model
        self.km = km
    
    def _calculate_mean_km(self) -> int:
        """
        Calculate the mean km of a vehicle based on its model year and mean km.

        Args:
            self

        Returns:
            int: The calculated mean km.
        """
        date = datetime.now()
        year = date.year
        years_difference = year - int(self.model)
        
        if years_difference == 0:
            return self.km
        
        return years_difference * Simulation_p_k.MEAN_KM
    
    def simulate_km(self, offset=0) -> int:
        """
        To generate the random data between a range 

        Args:
            self
            offset (int) : An int to change the random seed
        
        Returns:
            int : new km value
        """
        average_km = self._calculate_mean_km()
        np.random.seed(int(time.time()) % 100000 + offset)
        return np.random.randint(int(average_km*0.5), int(average_km*1.5))
    
    def calculate_percentage(self, km: int) -> float:
        """
        Calculate the percentage of the price based on the vehicle's Simulation_p_k.

        Args:
            self

        Returns:
            float: The calculated percentage.
        """

        average_km = self._calculate_mean_km()
        if km == None:
            return 1.0
        if average_km*Simulation_p_k.KM_THRESHOLD < km <= average_km :
            return 1.0
        elif km <= average_km * Simulation_p_k.KM_THRESHOLD:
            return 1.02
        
        else:
            increments: float = 0.0
            for increment in range(1,15):
                increments += 0.03
                if km <= (average_km +(Simulation_p_k.MEAN_KM * increment)):
                    return round(1 - increments, 2)
                
            return round(1 - Simulation_p_k.MAX_PENALTY,2)
        
    def calculate_price(self, km: int) -> int:
        """
        Calculate the price of the vehicle based on the given price and percentage.

        Args:
            self

        Returns:
            float: The calculated price.
        """
        new_price: float = self.price * self.calculate_percentage(km)
        # new_price = self.price - discount_value
        return round(new_price)



def generate_simulated_data(df, num_new_rows=5) -> pd.DataFrame:
    """
    Generates simulated data by applying a transformation based on specific columns.
    
    Args:
        df (pd.DataFrame): Input DataFrame with N columns.
        num_new_rows (int): Number of new rows to generate per existing row.
        
    Returns:
        pd.DataFrame: Original DataFrame concatenated with the simulated data.
    """
    new_rows = []
    
    # Ensure required columns exist
    required_cols = {"Kilometraje", "Modelo", "Pricing"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"The DataFrame must contain the columns: {required_cols}")

    # Identify other columns to keep (excluding Kilometraje, Modelo, Pricing)
    other_cols = [col for col in df.columns if col not in required_cols]

    for _, row in df.iterrows():
        km_orig, modelo, pr_orig = row["Kilometraje"], row["Modelo"], row["Pricing"]
        other_values = [row[col] for col in other_cols]  # Extract other column values

        if km_orig not in [0, 0.0]:  
            for i in range(num_new_rows): 
                simulation_obj = Simulation_p_k(pr_orig, modelo, km_orig)
                new_km = int(simulation_obj.simulate_km(i)) 
                price_new = simulation_obj.calculate_price(new_km)

                new_rows.append(other_values + [new_km, modelo, price_new])  

    df_new = pd.DataFrame(new_rows, columns=other_cols + ["Kilometraje", "Modelo", "Pricing"])
    return pd.concat([df, df_new], ignore_index=True)



def mean_km_f(mode: int , y = 'particular', fecha : datetime = datetime.now() ) -> int:
        """
        Calculate the mean km of a vehicle based on its model year and mean km.

        Args:
            mode (int) : Car year model
            fecha (datetime) : Fecha venta
        Returns:
            int: The calculated mean km.
        """
        if y == 'publico' or y == 'Público' or y == 'público' or y == 'Publico':
            MEAN_KM : int = 20000
        else:  
            MEAN_KM : int = 15000

        fecha = datetime.now()
        year = fecha.year
        years_difference = year - int(mode)
        
        if years_difference == 0:
            np.random.seed(int(time.time()) % 100000)
            return MEAN_KM - np.random.randint(0, MEAN_KM)
        
        return years_difference * MEAN_KM

if __name__ == '__main__':

    # To test the code 
    data = [['fase1', 'day1', 2020, 15e3, 500], ['fase2', 'day2', 2022,15e3*2, 300]]
    df = pd.DataFrame(data, columns=['F', 'D', 'Modelo', 'Kilometraje', 'Pricing'])
    df_simulated = generate_simulated_data(df, num_new_rows=5)
    print(df_simulated.head(12))
    print(df_simulated.shape)
