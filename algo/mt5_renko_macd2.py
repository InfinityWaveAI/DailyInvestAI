import MetaTrader5 as mt5
import os
import numpy as np
import pandas as pd
import datetime as dt
from stocktrends import Renko
import time
import copy

os.chdir("C:\\Users\\HP\\Downloads")
key = open("key.txt","r").read().split()
path=("C:\\Program Files\\MetaTrader 5\\terminal64.exe")

# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(login=int(key[0]),server=key[2],password=key[1]):
    print("initialize() failed, error code =",mt5.last_error())

pairs = ['EURUSD','GBPUSD','USDCHF','AUDUSD','USDCAD'] #currency pairs to be included in the strategy
pos_size = 0.5 #max capital allocated/position size for any currency pair. in MT5 the size is in unit of 10^5


def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy()
    df["MA_Fast"] = df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"] = df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
    df["Signal"] = df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df["MACD"],df["Signal"])

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L'] = abs(df['High'] - df['Low'])
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def renko_DF(DF):
    """Function to convert OHLC data into Renko bricks."""
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:, [0, 1, 2, 3, 4, 5]]
    df.columns = ["date", "open", "close", "high", "low", "volume"]

    # Renko transformation
    df2 = Renko(df)
    df2.brick_size = round(ATR(DF, 120)["ATR"].iloc[-1], 4)
    renko_df = df2.get_ohlc_data()

    # Add bar numbers
    renko_df["bar_num"] = np.where(
        renko_df["uptrend"] == True, 1, np.where(renko_df["uptrend"] == False, -1, 0)
    )
    renko_df = renko_df.copy()  # Explicit copy to avoid SettingWithCopyWarning

    # Correct cumulative bar_num calculation
    for i in range(1, len(renko_df)):
       if renko_df.loc[i, "bar_num"] > 0 and renko_df.loc[i - 1, "bar_num"] > 0:
           renko_df.loc[i, "bar_num"] += renko_df.loc[i - 1, "bar_num"]
       elif renko_df.loc[i, "bar_num"] < 0 and renko_df.loc[i - 1, "bar_num"] < 0:
           renko_df.loc[i, "bar_num"] += renko_df.loc[i - 1, "bar_num"]

    # Remove duplicate dates
    renko_df.drop_duplicates(subset="date", keep="last", inplace=True)
    
    return renko_df

def renko_merge(DF):
    """Function to merge Renko df with original OHLC df."""
    df = copy.deepcopy(DF)
    df["Date"] = df.index
    renko = renko_DF(df)
    renko.columns = ["Date", "open", "high", "low", "close", "uptrend", "bar_num"]

    # Convert 'Date' columns to datetime
    df["Date"] = pd.to_datetime(df["Date"])
    renko["Date"] = pd.to_datetime(renko["Date"])
    
    # Merge and forward-fill missing values
    merged_df = df.merge(renko.loc[:, ["Date", "bar_num"]], how="outer", on="Date")
    merged_df["bar_num"] = merged_df["bar_num"].ffill()
    merged_df["macd"] = MACD(merged_df, 12, 26, 9)[0]
    merged_df["macd_sig"] = MACD(merged_df, 12, 26, 9)[1]
    return merged_df

def get_position_df():
    positions = mt5.positions_get()
    if len(positions) > 0:
        pos_df = pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
        pos_df.time = pd.to_datetime(pos_df.time, unit="s")
        pos_df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        pos_df.type = np.where(pos_df.type==0,1,-1) #to distinguish between long and short positions
    else:
        pos_df = pd.DataFrame()
        
    return pos_df

def get_5m_candles(currency,lookback=10,bars=250):
    data = mt5.copy_rates_from(currency, mt5.TIMEFRAME_M5, dt.datetime.now() - dt.timedelta(10), 250)   
    data_df = pd.DataFrame(data) 
    data_df.time = pd.to_datetime(data_df.time, unit="s")
    data_df.set_index("time", inplace=True)
    data_df.rename(columns={"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"},inplace=True)
    return data_df

def place_market_order(symbol,vol,buy_sell,sl_pip,tp_pip):
    pip_unit = 10*mt5.symbol_info(symbol).point
    if buy_sell.capitalize()[0] == "B":
        direction = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - sl_pip*pip_unit
        tp = price + tp_pip*pip_unit
    else:
        direction = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
        sl = price + sl_pip*pip_unit
        tp = price - tp_pip*pip_unit
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": vol,
        "type": direction,
        "price": price,
        "sl": sl,
        "tp":tp,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    
    result = mt5.order_send(request)
    return result

def trade_signal(MERGED_DF,l_s):
    "function to generate signal"
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1]:
            signal = "Buy"
        elif df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1]:
            signal = "Sell"
            
    elif l_s == "long":
        if df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1]:
            signal = "Close_Sell"
        elif df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd"].tolist()[-2]>df["macd_sig"].tolist()[-2]:
            signal = "Close"
            
    elif l_s == "short":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1]:
            signal = "Close_Buy"
        elif df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd"].tolist()[-2]<df["macd_sig"].tolist()[-2]:
            signal = "Close"
    return signal
    

def main():
    try:
        open_pos = get_position_df()
        for currency in pairs:
            print(currency)
            long_short = ""
            if len(open_pos)>0:
                open_pos_cur = open_pos[open_pos["symbol"]==currency]
                if len(open_pos_cur)>0:
                    if (open_pos_cur.type * open_pos_cur.volume).sum() > 0:
                        long_short = "long"
                    elif (open_pos_cur.type * open_pos_cur.volume).sum() < 0:
                        long_short = "short"   
            
            ohlc = get_5m_candles(currency) 
            signal = trade_signal(renko_merge(ohlc),long_short)
    
            if signal == "Buy" or signal =="Sell":
                place_market_order(currency,pos_size,signal,sl_pip=10, tp_pip=20)
                print("New {} position initiated for {}".format(signal, currency))

            elif signal == "Close":
                tot_pos = (open_pos_cur.type * open_pos_cur.volume).sum()
                if tot_pos > 0:
                    place_market_order(currency,tot_pos,"Sell",sl_pip=10, tp_pip=20)
                elif tot_pos < 0:
                    place_market_order(currency,abs(tot_pos),"Buy",sl_pip=10, tp_pip=20)
                print("All positions closed for ", currency)
            elif signal == "Close_Buy":
                tot_pos = (open_pos_cur.type * open_pos_cur.volume).sum()
                place_market_order(currency,abs(tot_pos)+pos_size,"Buy",sl_pip=10, tp_pip=20)
                print("Existing Short position closed for ", currency)
                print("New long position initiated for ", currency)
            elif signal == "Close_Sell":
                tot_pos = (open_pos_cur.type * open_pos_cur.volume).sum()
                place_market_order(currency,tot_pos+pos_size,"Sell",sl_pip=10, tp_pip=20)
                print("Existing Long position closed for ", currency)
                print("New Short position initiated for ", currency)
    except Exception as e:
        print(e)
        print("error encountered....skipping this iteration")


# Continuous execution        
starttime=time.time()
timeout = time.time() + 60*60*1  # 60 seconds times 60 meaning the script will run for 1 hr
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time() - starttime) % 300.0)) # 5 minute interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
