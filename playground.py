import streamlit as st
import plotly.graph_objects as go

from training.utils.constants import ASSETS
from training.utils.indicators import ComputeRegistry
from training.utils.io import load_yf_data

selected_asset = st.sidebar.selectbox(
    'Asset', ASSETS.keys(), key='assets'
)

data = load_yf_data(ASSETS[selected_asset]['YF_TICKER'])

st.text(f"Total TimeStamps: {len(data)}")

st.table(data.tail(n=10))

st.title("Price")
fig = go.Figure(data=[
    go.Scatter(x=data.index, y=data['Adj Close'], name='Adjusted Close'),
])

indicators = st.sidebar.multiselect(
    "Technical Indicator",
    ["Momentum A", "Momentum B", 'Bollinger Bands'],
    ["Momentum A"],
)

for indicator in indicators:
    n_points = st.sidebar.number_input(indicator, min_value=1, max_value=len(data))
    indicator_df = ComputeRegistry.compute(indicator, data, n_points)
    fig.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['Adj Close'], name=indicator))
    if 'Adj Close_lower' in indicator_df.columns:
        fig = fig.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['Adj Close_lower'], name='Lower Band'))
    if 'Adj Close_upper' in indicator_df.columns:
        fig = fig.add_trace(go.Scatter(x=indicator_df.index, y=indicator_df['Adj Close_upper'], name='Upper Band'))

st.plotly_chart(fig)
