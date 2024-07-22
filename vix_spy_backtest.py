from backtesting import Backtest, Strategy
import pandas as pd
from stockstats import wrap 
from BloombergAPI import Bloomberg 
import datetime as dt 
from datetime import datetime
from datetime import date
import numpy as np 
from xbbg import blp

spx = blp.bdh(tickers=["SPX Index"], flds=["px_last", "px_high","px_low"], start_date = "2007-01-01")
spx.columns = spx.columns.droplevel()
spx.rename(columns={"px_last": "Close", "px_high": "High", "px_low": "Low"}, inplace=True)
# Dummy column for the wrapper
spx["Volume"] = 0
spx = wrap(spx)
rsi = spx.get('rsi')


vix = blp.bdh(tickers=["UX1 Index"], flds=["px_last", "px_high","px_low", "px_open"], start_date = "2007-01-01")
vix.columns = vix.columns.droplevel()
vix.rename(columns={"px_last": "Close", "px_high": "High", "px_low": "Low", "px_open": "Open"}, inplace=True)
df = vix.join(rsi, how='inner')
df.dropna(inplace=True)
df.drop(df[df["rsi"] == 100].index, inplace=True)


signal = pd.DataFrame(0, index=df.index, columns=["Signal"])
df = pd.concat([df, signal], axis=1)
rsi_90 = df.index[df["rsi"] > 80].to_list()
rsi_30 = df.index[df["rsi"] <= 59].to_list()
df.drop(df.columns[-2], axis=1, inplace=True)

df.loc[rsi_90, "Signal"] = 1
df.loc[rsi_30, "Signal"] = -1

df.index = pd.to_datetime(df.index)

class VIX_LS(Strategy):

    def init(self):
        pass
    def next(self):
        current_signal = self.data.Signal[-1]
        
        trades = self.trades
        def parse_trades(trades):
            for x in trades:
                a = x.entry_time
                b = self.data.index[-1]

                
                delta = b - a


                # Maximum hold period

                if delta.days > 1:
                    x.close()


        parse_trades(trades)
        if current_signal == 100:
        
            self.sell(size=1)
        
        elif current_signal == -1:
            
            self.buy(size=-100)

bt = Backtest(df, VIX_LS, cash=10000)
stats = bt.run()
print(stats)
bt.plot()