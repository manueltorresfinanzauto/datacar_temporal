import pandas as pd 
from tqdm import tqdm
from datetime import datetime
from sqlalchemy import create_engine, text
import time 
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm, tqdm_pandas
import re
import unicodedata
from tqdm import tqdm
from config.sqlacces import connection_str
from app.cleaners.motos import Motos


path_f = '/home/manueltorres/analitica-garaje/car_data_3.csv'
df = pd.read_csv(path_f)
print(df.shape)
df = Motos.find_motos(df)
print(df.shape)

df.to_csv('../car_data_v1_3.csv', index=False)
