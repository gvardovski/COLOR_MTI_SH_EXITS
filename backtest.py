import pandas as pd
import vectorbt as vbt
import pandas_ta as ta
import numpy as np
import yaml
from savetopdf import save_backtesting_results_to_pdf
from makemetricpng import create_heatmap

def processdata(config):
    df_day = pd.read_csv(config['Data_filename_day'], parse_dates=['Time'], index_col='Time')
    df_day.drop(columns=['Volume', 'Change', 'ChangePercent', 'Vwap'], inplace=True)
    df_day['SMA20'] = ta.sma(df_day['Close'], length=20)
    df_day['SMA50'] = ta.sma(df_day['Close'], length=50)
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

def backtest(df_day):

    index_arr_day = df_day.index.to_numpy()
    close_arr_day = df_day['Close'].to_numpy()
    color_arr_day = df_day['Color'].to_numpy()
    ch_exit_arr_day = df_day['Ch_exit'].to_numpy()
    entry_arr_day = np.full(len(index_arr_day), False)
    exit_arr_day = np.full(len(index_arr_day), False)
    price_arr_day = np.full(len(index_arr_day), np.nan)

    trade_is_open = False
    close_price = np.nan

    for i in range(1, len(index_arr_day)):
        if not trade_is_open and color_arr_day[i] == 'G':
            trade_is_open = True
            entry_arr_day[i] = True
            close_price = ch_exit_arr_day[i]
            price_arr_day[i] = close_arr_day[i]
        elif trade_is_open:
            if (close_arr_day[i] > close_price):
                stop = i + config['Days'] + 1
                if (stop >= len(index_arr_day)):
                    continue
                go_throw = True
                for j in range(i, stop):
                    if (j >= len(index_arr_day)):
                        break
                    if (close_arr_day[j] < close_price):
                        go_throw = False
                        break
                if go_throw:
                    trade_is_open = False
                    exit_arr_day[j] = True
                    close_price = None
                    price_arr_day[j] = close_arr_day[j]
            else:
                continue
        else:
                continue

    pf = vbt.Portfolio.from_signals(
    entries = entry_arr_day,
    exits = exit_arr_day,
    price = price_arr_day,
    open = df_day["Open"],
    close = close_arr_day,
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

    # rezults = []
    for i in range(1, config['Days']+1):
        pf = backtest(df_day)

        # stats = pf.stats().to_dict()
        # stats.update({'Days': i})
        # rezults.append(stats)

        file_path = config['Data_filename_day'].split('.')[0]
        file_path = (f"{file_path}_{i}_days")
        save_backtesting_results_to_pdf(pf, file_path)
    
    # optimization_df = pd.DataFrame(rezults)
    # print(optimization_df.columns)
    # print(f"CSV file with optimization '{file_path}_optimization.CSV' was created!")
    # create_heatmap(optimization_df, metric_name='Total Return [%]', index_col='Days', column_col='')