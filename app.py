import streamlit as st
import pandas as pd
from estrategia import simular_sesion
from utils import calcular_rsi
from utils import obtener_velas_twelvedata
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

fig = None
st.set_page_config(page_title="Simulador Reversión Martingala", layout="wide")
# Refresca cada 30 segundos (30,000 ms)
st_autorefresh(interval=30 * 1000, key="data_refresh")
st.title("🔁 Simulador de Reversión con Martingala")

# Parámetros
payout = st.sidebar.slider("Payout", 0.7, 0.95, 0.87, 0.01)
stake_pct = st.sidebar.slider("Stake base (% balance)", 0.5, 5.0, 1.0, 0.1)
martingala = st.sidebar.slider("Multiplicador Martingala", 1.0, 2.0, 1.15, 0.05)
ciclos_max = st.sidebar.slider("Ciclos máximos", 1, 6, 4)
take_profit = st.sidebar.slider("Take Profit diario (%)", 1, 20, 10)
stop_loss = st.sidebar.slider("Stop Loss diario (%)", 1, 20, 10)
filtro_rsi = st.sidebar.checkbox("Usar filtro RSI 40–60", value=False)

# Carga de velas
st.subheader("📄 Cargar secuencia de velas")


# Checkbox para usar gráfico real
usar_twelvedata = st.sidebar.checkbox("📡 Usar gráfico real de Twelve Data")
# Selector de símbolo de divisa
moneda = st.sidebar.selectbox(
    "💱 Par de divisas",
    options=["EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "USD/CHF"],
    index=0
)
if usar_twelvedata:
    df = obtener_velas_twelvedata(symbol=moneda, limit=100)
    if df.empty:
        st.warning("⚠️ No se pudieron obtener datos desde Twelve Data.")
    else:
        st.success("✅ Datos reales cargados desde Twelve Data")
        st.info(f"🔎 Analizando **{moneda}** ")
else:
    archivo = st.file_uploader("📄 Sube un .csv con columna 'color' (roja/verde)", type="csv")
    if archivo:
        df = pd.read_csv(archivo)
    else:
        df = pd.read_csv("data/velas_demo.csv")
        
# Crear gráfico de velas para cualquier df válido
if not df.empty and {"open", "close"}.issubset(df.columns):
    df["high"] = df[["open", "close"]].max(axis=1) + 0.0003
    df["low"] = df[["open", "close"]].min(axis=1) - 0.0003

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color="green",
        decreasing_line_color="red",
        showlegend=False
    )])

    fig.update_layout(xaxis_rangeslider_visible=False, height=400)


if filtro_rsi:
    df['RSI'] = calcular_rsi(df['color'], periodo=6)

# Ejecutar simulación
resultado = simular_sesion(
    df,
    payout=payout,
    stake_pct=stake_pct / 100,
    martingala=martingala,
    ciclos_max=ciclos_max,
    tp_pct=take_profit / 100,
    sl_pct=stop_loss / 100,
    usar_rsi=filtro_rsi
)

# Añadir marcadores reales si hay entradas válidas
if fig and resultado.get("entradas_idx"):
    '''
    fig.add_trace(go.Scatter(
        x=resultado["entradas_idx"],
        y=df.loc[resultado["entradas_idx"], "close"],
        mode="markers",
        marker=dict(
            size=10,  # más pequeño
            color="rgba(30, 144, 255, 0.8)",  # azul translúcido (dodgerblue, 50%)
            symbol="x"
        ),
        name="Entradas reales"
    ))

    fig.add_trace(go.Scatter(
        x=resultado["entradas_filtradas_idx"],
        y=df.loc[resultado["entradas_filtradas_idx"], "close"],
        mode="markers",
        marker=dict(
            size=10,
            color="rgba(255, 140, 0, 0.8)",  # naranja con transparencia
            symbol="triangle-down"
        ),
        name="Filtradas por RSI"
    ))

    colores_por_ciclo = {1: "limegreen", 2: "gold", 3: "orangered", 4: "crimson", 5: "black", 6: "purple"}
    
    for idx, ciclo in zip(resultado["entradas_idx"], resultado["ciclos_por_entrada"]):
        color = colores_por_ciclo.get(ciclo, "gray")
        fig.add_trace(go.Scatter(
            x=[idx],
            y=[df.loc[idx, "close"] + 0.0005],
            mode="markers",
            marker=dict(size=5, color=color, symbol="circle"),
            name=f"Ciclo {ciclo}",
            hovertemplate=f"Ciclo {ciclo}<br>Índice: {idx}<extra></extra>"
        ))
    '''
    
    for idx, pred in zip(resultado["entradas_idx"], resultado["predicciones"]):
        color = "red" if pred == "roja" else "green"
        simbolo = "triangle-down" if pred == "roja" else "triangle-up"
        distancia = 0.0005 if pred == "roja" else -0.0005
    
        fig.add_trace(go.Scatter(
            x=[idx],
            y=[df.loc[idx, "close"] + distancia],
            mode="markers",
            marker=dict(size=9, color=color, symbol=simbolo),
            name=f"Predicción {pred}",
            hovertemplate=f"Predicción: {pred}<br>Índice: {idx}<extra></extra>"
        ))


if fig:
    st.subheader("📊 Gráfico con Entradas Detectadas")
    st.plotly_chart(fig, use_container_width=True)



# Mostrar resultados
st.subheader("📊 Resultados")
st.metric("Entradas totales", resultado['entradas'])
if filtro_rsi:
    st.metric("Filtradas por RSI", resultado['entradas_filtradas_rsi'])

st.metric("Acertadas", resultado['aciertos'])
prom = resultado.get('prom_ciclos')
st.metric("Ciclos promedio", f"{prom:.2f}" if prom is not None else "–")
st.metric("Saldo final", f"${resultado['saldo_final']:.2f}")
st.metric("Drawdown máximo", f"{resultado['drawdown_max']:.2f}%")
st.line_chart(resultado['historial'])
