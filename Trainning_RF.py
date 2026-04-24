import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from modelos_prueba.tunning_train_RF import tt_randomforest
from modelos_prueba.columns_check import columns_model
import time

from datetime import datetime


path = r'../car_data_V_1_5_2026_01_14.csv'
print('-------------------------')

df = columns_model(path)
print(df.shape)
print(df.columns.to_list())
print(df.head())


tt_randomforest(df) 



