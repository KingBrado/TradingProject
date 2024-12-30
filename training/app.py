import streamlit as st
import pandas as pd

from utils.constants import ASSETS
from utils.strategy import StrategyRegistry
from utils.io import load_strategy_config,  load_yf_data
import plotly.graph_objects as go

data = load_yf_data(ASSETS['TESLA']['YF_TICKER'])

select_strategy = st.selectbox('Strategy', ['crossover'], format_func=str.title)
pct_val = st.select_slider('Size of Backtesting Set', range(0, 105, 5), value=10)

total_len = len(data['Adj Close'])
train_data_idx = int((1-pct_val/100) * total_len)

train_data = data['Adj Close'].iloc[:train_data_idx]
val_data = data['Adj Close'].iloc[train_data_idx:]

params = load_strategy_config(select_strategy)
strategy = StrategyRegistry.get_strategy(select_strategy, params)
strategy.fit(train_data)
m_mean = train_data.rolling(strategy._m).mean()
m_mean.name = 'm_mean'
n_mean = train_data.rolling(strategy._n).mean()
n_mean.name = 'n_mean'

df = pd.concat([train_data, m_mean, n_mean], axis=1).dropna()

fig = go.Figure(data=[
    go.Scatter(x=df.index, y=df['Adj Close'], name='Adj Close'),
    go.Scatter(x=df.index, y=df['m_mean'], name='Short average'),
    go.Scatter(x=df.index, y=df['n_mean'], name='Long Average')
])

st.plotly_chart(fig)

pred_ret = strategy.predict(val_data)

st.text(f"Predicted Return on Backtesting Data: {pred_ret:.4f}")

m_mean = val_data.rolling(strategy._m).mean()
m_mean.name = 'm_mean'
n_mean = val_data.rolling(strategy._n).mean()
n_mean.name = 'n_mean'

df = pd.concat([val_data, m_mean, n_mean], axis=1).dropna()

fig = go.Figure(data=[
    go.Scatter(x=df.index, y=df['Adj Close'], name='Adj Close'),
    go.Scatter(x=df.index, y=df['m_mean'], name='Short Average'),
    go.Scatter(x=df.index, y=df['n_mean'], name='Long Average')
])

st.plotly_chart(fig)