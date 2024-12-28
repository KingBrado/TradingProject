import pandas as pd
import yfinance as yf
import yaml

def load_yf_data(ticker: str) -> pd.DataFrame:
    print(ticker)
    data = yf.download(ticker, period='2y', interval='1d', multi_level_index=False)
    data.index = data.index.strftime('%Y-%m-%d')
    return data


def load_strategy_config(strategy: str) -> dict:
    with open('training/config/strategies.yaml') as file:
        params = yaml.safe_load(file)
    return params[strategy]['params']