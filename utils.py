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


def obtener_velas_yf(ticker="EURUSD=X", interval="1m", period="1d", limit=100):
    df = yf.download(ticker, interval=interval, period=period, progress=False)

    # Verifica si tiene datos y columnas necesarias
    if df.empty or not set(["Open", "Close"]).issubset(df.columns):
        return pd.DataFrame(columns=["Open", "Close", "color"])

    df = df.dropna(subset=["Open", "Close"])
    if df.empty:
        return pd.DataFrame(columns=["Open", "Close", "color"])

    df = df.tail(limit).copy()
    df["color"] = df.apply(lambda row: "verde" if row["Close"] > row["Open"] else "roja", axis=1)
    return df[["Open", "Close", "color"]].reset_index(drop=True)




