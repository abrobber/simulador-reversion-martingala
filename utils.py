import requests
import pandas as pd
import streamlit as st
import yfinance as yf

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

def obtener_velas_twelvedata(symbol="EUR/USD", interval="1min", apikey="7a8323602dee4ac382196181cc32a8a7", limit=100):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": limit,
        "apikey": apikey
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if "values" not in data:
            return pd.DataFrame(columns=["open", "close", "color"])

        df = pd.DataFrame(data["values"])
        df["open"] = df["open"].astype(float)
        df["close"] = df["close"].astype(float)
        df["color"] = df.apply(lambda row: "verde" if row["close"] > row["open"] else "roja", axis=1)
        return df[["open", "close", "color"]].iloc[::-1].reset_index(drop=True)

    except Exception as e:
        print(f"Error al obtener datos de Twelve Data: {e}")
        return pd.DataFrame(columns=["open", "close", "color"])





