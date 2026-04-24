import pandas as pd 
from tqdm import tqdm
from datetime import datetime
from sqlalchemy import create_engine, text
import time 
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm, tqdm_pandas

# Personal 
from app import general_clean



