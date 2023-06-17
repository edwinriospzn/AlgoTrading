#Backtesting MACD

from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs
# from reg_lin_bt import Robots_Ur
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import pandas_ta as pdta
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplfinance as mpf


nombre = 94603449
clave = 'gkpvlsn0'
servidor = 'InstaForex-Server'
path = r'C:\Program Files\InstaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

#Aquí definimos los indicadores para el backtest
def i_adx(data, length):
    adx = pdta.adx(high = pd.Series(data.High), low = pd.Series(data.Low), close = pd.Series(data.Close), length=length)
    return adx.to_numpy().T

def i_dpo(data, length):
    dpo = pdta.dpo(close = pd.Series(data.Close), length=length, centered=False)
    return dpo.to_numpy().T

#Revisar si se debe tener en cuenta la longitud
def i_p_sar(data):
    p_sar = pdta.psar(high = pd.Series(data.High), low = pd.Series(data.Low), close = pd.Series(data.Close))
    return p_sar.to_numpy().T

def i_donchian(data, length):
    donchian = pdta.donchian(high = pd.Series(data.High), low = pd.Series(data.Low), lower_length =length, upper_length=length)
    return donchian.to_numpy().T

def i_macd(data, fast, slow, signal):
    macd = pdta.macd(close = pd.Series(data.Close), fast=fast, slow = slow, signal = signal)
    return macd.to_numpy().T

def i_atr(data, length):
    atr = pdta.atr(high = pd.Series(data.High), low = pd.Series(data.Low), close = pd.Series(data.Close), length=length)
    return atr.to_numpy().T


class MACD_Strategy(Strategy):    

#Win rate Opti: 45-30-5-160
#Return % Opti: 45-30-20-150
#Sortino Opti: 45-30-20-110

    fast_macd = 30
    slow_macd = 45
    signal_macd = 20

    period_sma = 150
    period_ema = 110


    periodo_donchian = 10
    periodo_atr = 14
    periodo_rsi = 14
    factor_donchian = 3
    factor_sl_donchian_long = 1
    factor_sl_donchian_short = 1

    def init(self):

        #Precios
        self.prices_close = self.data.Close
        self.prices_high = self.data.High
        self.prices_low = self.data.Low
        self.prices_open = self.data.Open

        #MACD
        self.macd = self.I(i_macd, self.data, self.fast_macd, self.slow_macd, self.signal_macd)
        self.macd_h = self.macd[1]
        self.macd_line = self.macd[0]

        #Médias Móviles
        self.sma = self.I(pdta.sma, pd.Series(self.prices_close), self.period_sma)
        self.ema = self.I(pdta.ema, pd.Series(self.prices_close), self.period_ema)

        #Parabolic SAR
        self.psar = self.I(i_p_sar, self.data)        
        self.psarl = self.psar[0]
        self.psars = self.psar[1]

        #Donchian
        self.donchian = self.I(i_donchian, self.data, self.periodo_donchian)
        self.donchian_l = self.donchian[0]        
        self.donchian_u = self.donchian[2]

        #ATR
        self.atr = self.I(pdta.atr, pd.Series(self.prices_high), pd.Series(self.prices_low), pd.Series(self.prices_close), self.periodo_atr)
        self.sl_atr_long = self.prices_close - self.atr
        self.sl_atr_short = self.prices_close + self.atr

        #RSI
        self.rsi = self.I(pdta.rsi, pd.Series(self.prices_close), self.periodo_rsi)


# tp=self.tp_donchian_short
# tp=1.00000001*self.tp_donchian_long
        self.tp_donchian_long = (self.factor_donchian * abs((self.donchian_l - self.prices_close))) + self.prices_close
        self.tp_donchian_short = -(self.factor_donchian * abs((self.donchian_u - self.prices_close))) + self.prices_close

  
    def next(self):

        if self.macd_h[-2]<0 and self.macd_h[-1]>0 and self.ema[-1] < self.prices_close[-1] and self.macd_line<0:
            self.position.close()
            self.buy(sl=self.donchian_l*self.factor_sl_donchian_long)
            
        elif self.macd_h[-2]>0 and self.macd_h[-1]<0 and self.ema[-1] > self.prices_close[-1] and self.macd_line>0:
            self.position.close()
            self.sell(sl= self.donchian_u*self.factor_sl_donchian_short)

simbolo = 'AUDUSD'

data = bfs.get_data_for_bt(mt5.TIMEFRAME_M15, simbolo,17280)
data2 = data.head(17280)

bt = Backtest(data2,MACD_Strategy,cash = 100_000)
stats_3 = bt.run()
trades = stats_3._trades

trades['Duration'].mean()
trades[trades['PnL']>0]['Duration'].mean()
trades[trades['PnL']<0]['Duration'].mean()

print(stats_3)

# bt.plot()

plt.style.use('seaborn-darkgrid')
plt.hist(trades['PnL'], bins=50, edgecolor='black')
# plt.xlim(-1000, 4000)
plt.xlabel('Ganancia')
plt.ylabel('Frecuencia')
plt.title('Distribución de PnL/Trade')
plt.grid(True)

# Format x-axis as currency
formatter = ticker.FormatStrFormatter('$%1.0f')  # Change the number of decimal places if needed
plt.gca().xaxis.set_major_formatter(formatter)

plt.gca().spines['top'].set_visible(True)
plt.gca().spines['right'].set_visible(True)
plt.gca().spines['bottom'].set_visible(True)
plt.gca().spines['left'].set_visible(True)
plt.axvline(x=0, color='red', linestyle='--')



# # Gráficas

# punto_inicio = 460
# punto_final = punto_inicio +200

# mpf.plot(data[punto_inicio:punto_final]
#         ,type = 'candle', style = 'charles'
#         # ,volume = True
#         ,title = simbolo
#         ,hlines=dict(vlines=data['Close'].iloc[punto_inicio]
#                             # ,data['sl_long'].iloc[punto_inicio]
#                             # ,data['tp_long'].iloc[punto_inicio])
#                             # ,colors=['r','g','b']
#                             ,linestyle='dotted'
#                             ,linewidths=(3,4))
#         # ,mav = (50)
#         # ,alines = two_points
#         # ,addplot = apds
#         )





# for valor in [30000,40000,50000,60000]:
#     data = bfs.get_data_for_bt(mt5.TIMEFRAME_M15,'EURUSD.fx',valor)
#     data2 = data.head(10000)
#     backtesting_4 = Backtest(data2,MACD_Strategy,cash = 10_000)
#     stats_4 = backtesting_4.run()


# stats_3, hm = bt.optimize(
#                         slow_macd = range(10, 50, 5),
#                         fast_macd = range(30, 80, 5),
#                         signal_macd = range(5,25, 5),
#                         period_ema = range(100,300,10),
#                         # factor_sl_donchian_long = [0.99, 0.991, 0.992, 0.993, 0.994, 0.995, 0.996, 0.997, 0.998, 0.999, 1],
#                         # factor_sl_donchian_short = [1, 1.001, 1.002, 1.003, 1.004, 1.005, 1.006, 1.007, 1.008, 1.009, 1.01],
#                         return_heatmap= True,
#                         constraint= lambda param: param.fast_macd < param.slow_macd,
#                         maximize = 'Sortino Ratio')
















#constraint = lambda param: param.xxxxx > param.yyyyyy


# for valor in [30000,40000,50000,60000]:
#     data = bfs.get_data_for_bt(mt5.TIMEFRAME_M15,'EURUSD.fx',valor)
#     data2 = data.head(10000)
#     backtesting_4 = Backtest(data2,Strategy_reg,cash = 100_000)
#     stats_4 = backtesting_4.run()

#     print('############################################')

#     print(stats_4)