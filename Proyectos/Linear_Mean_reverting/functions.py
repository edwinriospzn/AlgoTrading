import MetaTrader5 as mt5
import pandas as pd

def extract_data(par:str,periodo:mt5,cantidad:int, nombre, clave, servidor, path) -> pd.DataFrame:
    '''
    Función para extraer los datos de MT5 y convertitlos en un DataFrame

    # Parámetros 
    
    - par: Símbolo
    - periodo: M1, M5...etc
    - cantidad: Entero con el número de registros a extraer

    '''
    mt5.initialize(login = nombre, password = clave, server = servidor, path = path)
    rates = mt5.copy_rates_from_pos(par, periodo, 0, cantidad)  
    tabla = pd.DataFrame(rates)
    tabla['time']=pd.to_datetime(tabla['time'], unit='s')

    return tabla