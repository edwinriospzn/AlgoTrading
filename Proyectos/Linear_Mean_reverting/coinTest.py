import pandas as pd
import MetaTrader5 as mt5
import numpy as np
from functions import *
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

sp500 =extract_data('.US500Cash', mt5.TIMEFRAME_M1, 2000, nombre, clave, servidor, path)
nasdaq =extract_data('.USTECHCash', mt5.TIMEFRAME_M1, 2000, nombre, clave, servidor, path)
jp =extract_data('.JP225Cash', mt5.TIMEFRAME_M1, 2000, nombre, clave, servidor, path)

Y = pd.DataFrame([sp500['close'], nasdaq['close'], jp['close']]).T
Y.columns = ['sp500', 'nasdaq', 'jp']

jres = coint_johansen(Y, det_order=0, k_ar_diff=1)

jres.evec

X = Y.to_numpy()
y = np.matmul(X, np.array(jres.evec[1]))


