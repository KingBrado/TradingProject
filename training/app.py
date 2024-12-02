import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Titolo dell'applicazione
st.title("Scarica Dati Finanziari")

# Box 
st.write("Seleziona i simboli finanziari:")
symbols = st.multiselect(
    "Simboli disponibili:",
    options=["AAPL", "NVDA", "TSLA"],
    default=["AAPL"]
)
intervals = st.selectbox(
    "Intervalli disponibili sono:",
    options=["1m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
)
days = st.selectbox(
    "Seleziona periodo:",
    options=[30, 60, 120, 160],
)
strategies = st.multiselect(
    "Seleziona strategia:",
    options=["Crossover", "OrderFlow", "RSI divergence","Volume Weight Average Price"],
)
# Periodo
end_date = datetime.today()
start_date = end_date - timedelta(days=days)

# Funzione per scaricare i dati
def fetch_data(symbols):
    all_data = pd.DataFrame()

    for symbol in symbols:
        st.write(f"Scaricando i dati per: {symbol}")
        data = yf.download(symbol, start=start_date, end=end_date, interval=intervals)
        
        if data.empty:
            st.warning(f"Nessun dato trovato per {symbol}.")
            continue
        
        # Aggiunta del simbolo nei dati per tracciarne l'origine
        data["Symbol"] = symbol
        
        # Aggregazione dei dati
        all_data = pd.concat([all_data, data])

    return all_data

# Pulsante per avviare il processo
if st.button("Scarica e Visualizza Dati"):
    if not symbols:
        st.warning("Seleziona almeno un simbolo.")
    else:
        data = fetch_data(symbols)
        if not data.empty:
            st.write("Ecco i dati aggregati:")
            st.dataframe(data)
            st.write("Grafico di tutti i dati (Open, High, Low, Close):")
            st.line_chart(data[["Open", "High", "Low", "Close"]])
        else:
            st.warning("Nessun dato disponibile per i simboli selezionati.")
