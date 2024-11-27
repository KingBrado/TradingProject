import streamlit as st
import yfinance as yf
import pandas as pd
from utils.constants import ASSETS
import plotly.graph_objects as go


st.cache_data
def load_yf_data(ticker: str) -> pd.DataFrame:
    data = yf.download(ticker, period='2y', interval='1h')
    data = data.droplevel(1, axis=1)
    return data

selected_asset = st.selectbox(
    'Asset', ASSETS.keys(), key='assets'
)

data = load_yf_data(ASSETS[selected_asset]['YF_TICKER'])

st.text(f"Total TimeStamps: {len(data)}")

st.table(data.tail(n=10))

st.title("Price")
fig = go.Figure(data=go.Scatter(x=data.index, y=data['Adj Close']))

st.plotly_chart(fig)