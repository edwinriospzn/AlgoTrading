import os 
import MetaTrader5 as mt5
import pandas as pd

name = 67043467
password = 'Genttly.2022'
server = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

timeframes = {
    'M1': mt5.TIMEFRAME_M1, 
    'M5': mt5.TIMEFRAME_M5, 
    'M10': mt5.TIMEFRAME_M10, 
    'M15': mt5.TIMEFRAME_M15,
    'M30': mt5.TIMEFRAME_M30,
    'H1': mt5.TIMEFRAME_H1
    }

symbols = ['EURUSD', 'GBPUSD', 'USDCAD', 'AUDUSD', 'EURGBP']

mt5.initialize(login = name, password = password, server = server, path = path)

def get_data(symbol: str, timeframe: mt5, num_periods: int):
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_periods)  
    tabla = pd.DataFrame(rates)
    tabla['time']=pd.to_datetime(tabla['time'], unit='s')

    return tabla

times = timeframes.keys()

for s in symbols:
    for t in times:
        mt5_time = timeframes[t]
        df = get_data(s, mt5_time, 10000)

        root_folder = 'Data/' 
        symbol_folder = root_folder + s  + '/' 

        file_name = s + '_' + t + '.csv'

        file = symbol_folder + '/' + file_name

        if not os.path.exists(symbol_folder):
            os.mkdir(symbol_folder)

        df.to_csv(file, sep=';', index=False)

