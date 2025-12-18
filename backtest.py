import pandas as pd
import re
import vectorbt as vbt
import numpy as np
import yaml
from savetopdf import save_backtesting_results_to_pdf

def get_time_interval(config):
   
    start_date = pd.to_datetime(config['Time_interval']['start_date']).normalize()
    end_date = pd.to_datetime(config['Time_interval']['end_date']).normalize()
    return start_date, end_date


def processdata(config):
    df_day = pd.read_csv(config['Data_filename_day'], parse_dates=['Time'], index_col='Time')
    start_date, end_date = get_time_interval(config)
    df_day = df_day[(df_day.index >= start_date) & (df_day.index <= end_date)]
    df_day.drop(columns=['Volume'], inplace=True)
    df_day['SMA20'] = df_day['Close'].rolling(window=20).mean()
    df_day['SMA50'] = df_day['Close'].rolling(window=50).mean()
    df_day.dropna(inplace=True)
    df_day['Color'] = 'Y'
    df_day.loc[df_day['SMA20'] < df_day['SMA50'],'Color'] = 'R'
    df_day.loc[(df_day['SMA20'] > df_day['SMA50']) & (df_day['Close'] > df_day['SMA20']) & (df_day['SMA20'] > df_day['SMA20'].shift(7)),'Color'] = 'G'
    df_day.drop(columns=['SMA20', 'SMA50'], inplace=True)

    return df_day

def chandelier_exit(df_day, length=22, mult=3.0, use_close=True):
        
    df = df_day.copy()
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.ewm(alpha=1/length, adjust=False).mean()
    atr_mult = mult * atr
    
    if use_close:
        highest = close.rolling(window=length).max()
    else:
        highest = high.rolling(window=length).max()
    
    long_stop = highest - atr_mult
    
    long_stop_prev = long_stop.shift(1)
    close_prev = close.shift(1)
    
    for i in range(1, len(long_stop)):
        if pd.notna(long_stop_prev.iloc[i]) and pd.notna(close_prev.iloc[i]):
            if close_prev.iloc[i] > long_stop_prev.iloc[i]:
                long_stop.iloc[i] = max(long_stop.iloc[i], long_stop_prev.iloc[i])
    
    df['Ch_exit'] = long_stop
    df.dropna(inplace=True)

    return df

def backtest(df_day, nday):

    # index_arr_day = df_day.index.to_numpy()
    # close_arr_day = df_day['Close'].to_numpy()
    # color_arr_day = df_day['Color'].to_numpy()
    # ch_exit_arr_day = df_day['Ch_exit'].to_numpy()
    # entry_arr_day = np.full(len(index_arr_day), False)
    # exit_arr_day = np.full(len(index_arr_day), False)
    # price_arr_day = np.full(len(index_arr_day), np.nan)

    # trade_is_open = False
    # close_price = np.nan

    # for i in range(0, len(index_arr_day)):
    #     if not trade_is_open and color_arr_day[i] == 'G':
    #         trade_is_open = True
    #         entry_arr_day[i] = True
    #         close_price = ch_exit_arr_day[i]
    #         price_arr_day[i] = close_arr_day[i]
    #     elif trade_is_open and close_arr_day[i] < close_price:
    #         go_throw = -1
    #         for j in range(0, nday + 1):
    #             if close_arr_day[i + j] < close_price:
    #                 go_throw += 1
    #             if go_throw == nday:
    #                 print(f"J = {j}")
    #                 trade_is_open = False
    #                 exit_arr_day[i + j] = True
    #                 close_price = np.nan
    #                 price_arr_day[i + j] = close_arr_day[i + j]

    close_arr = df_day['Close'].to_numpy()
    color_arr = df_day['Color'].to_numpy()
    ch_exit_arr = df_day['Ch_exit'].to_numpy()

    n = len(df_day)
    entry_arr = np.zeros(n, dtype=bool)
    exit_arr = np.zeros(n, dtype=bool)
    price_arr = np.full(n, np.nan)

    trade_is_open = False
    close_price = np.nan
    count = -1

    for i in range(n):
        if not trade_is_open and color_arr[i] == 'G':
            trade_is_open = True
            entry_arr[i] = True
            close_price = ch_exit_arr[i]
            price_arr[i] = close_arr[i]
            count = -1
            continue
        if trade_is_open:
            if close_arr[i] < close_price:
                count += 1
            else:
                count = -1

            if count == nday:
                trade_is_open = False
                exit_arr[i] = True
                price_arr[i] = close_arr[i]
                close_price = np.nan
                count = -1

    pf = vbt.Portfolio.from_signals(
    entries = entry_arr,
    exits = exit_arr,
    price = price_arr,
    open = df_day["Open"],
    close = close_arr,
    size = config['Trade']['size'],
    size_type = config['Trade']['size_type'],
    init_cash = config['Initial_cash'],
    freq = '1d'
    )

    return pf

if __name__ == "__main__":
    
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    df_day = processdata(config)
    df_day = chandelier_exit(df_day, use_close=False)

    start_date, end_date = get_time_interval(config)
    file_path = config['Data_filename_day'].split('.')[0]
    split_do = file_path.split('[')[0]
    split_po = file_path.split(']',1)[1]
    split_po = split_po.split(']')[1]
    file_path = f"{split_do}[{start_date.date()}][{end_date.date()}]{split_po}"

    for j in range(0, config['Days'] + 1):
        pf = backtest(df_day, j)

        save_backtesting_results_to_pdf(pf, f"{file_path}_{j}_days")