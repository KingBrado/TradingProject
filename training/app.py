import streamlit as st

from utils.constants import ASSETS
from utils.strategy import StrategyRegistry
from utils.io import load_strategy_config,  load_yf_data

data = load_yf_data(ASSETS['TESLA']['YF_TICKER'])

select_strategy = st.selectbox('Strategy', ['crossover'], format_func=str.title)
pct_val = st.select_slider('Size of Backtesting Set', range(0, 105, 5), value=10)


params = load_strategy_config(select_strategy)
strategy = StrategyRegistry.get_strategy(select_strategy, params)
strategy.fit(data['Adj Close'])
