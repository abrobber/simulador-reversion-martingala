import requests
import pandas as pd
import streamlit as st

def calcular_rsi(colores, periodo=6):
    import numpy as np
    delta = [1 if colores[i] != colores[i-1] else -1 for i in range(1, len(colores))]
    delta = [0] * (len(colores) - len(delta)) + delta
    rsi = []
    for i in range(len(delta)):
        if i < periodo:
            rsi.append(50)
        else:
            sub = delta[i-periodo+1:i+1]
            gains = sum(d for d in sub if d > 0)
            losses = abs(sum(d for d in sub if d < 0))
            rs = gains / losses if losses != 0 else 1
            rsi.append(100 - (100 / (1 + rs)))
    return rsi

def obtener_velas_binance(symbol="EURUSDT", interval="1m", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if not data or not isinstance(data, list) or len(data[0]) < 6:
            st.warning("⚠️ Binance devolvió datos vacíos o con formato inesperado.")
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["open"] = df["open"].astype(float)
        df["close"] = df["close"].astype(float)
        df["color"] = df.apply(lambda row: "verde" if row["close"] > row["open"] else "roja", axis=1)

        if df.empty:
            st.warning("⚠️ No se generaron velas válidas.")
        return df[["open", "close", "color"]]

    except requests.exceptions.RequestException as e:
        st.error(f"🚫 Error al conectar con Binance: {e}")
        return pd.DataFrame()

