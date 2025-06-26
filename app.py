import streamlit as st
import pandas as pd
from estrategia import simular_sesion
from utils import calcular_rsi
from utils import obtener_velas_twelvedata
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Reversión Martingala", layout="wide")
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
usar_twelvedata = st.sidebar.checkbox("📡 Usar gráfico real de Twelve Data (EUR/USD)")

if usar_twelvedata:
    @st.cache_data(ttl=60)
    df = obtener_velas_twelvedata(limit=100)
    if df.empty:
        st.warning("⚠️ No se pudieron obtener datos desde Twelve Data.")
    else:
        st.success("✅ Datos reales cargados desde Twelve Data")
        if not df.empty:
            st.subheader("📊 Gráfico de Velas (Candlestick)")
        
            # Estimar high y low si no se tienen (porque Twelve sólo da open/close)
            df["high"] = df[["open", "close"]].max(axis=1) + 0.0003  # margen arriba
            df["low"] = df[["open", "close"]].min(axis=1) - 0.0003   # margen abajo
        
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                increasing_line_color='green',
                decreasing_line_color='red',
                showlegend=False
            )])
        
            fig.update_layout(xaxis_rangeslider_visible=False, height=400)
            #st.plotly_chart(fig, use_container_width=True)

            # Detectar entradas según patrón de reversión simple
            entradas_idx = []
            for i in range(2, len(df)):
                if df["color"][i-2] == df["color"][i-1] and df["color"][i] != df["color"][i-1]:
                    entradas_idx.append(i)
            
            # Agregar marcadores en el gráfico donde hay entrada
            fig.add_trace(go.Scatter(
                x=entradas_idx,
                y=df.loc[entradas_idx, "close"],
                mode="markers",
                marker=dict(size=10, color="dodgerblue", symbol="circle"),
                name="Entrada detectada"
            ))
            
            # Mostrar gráfico actualizado
            st.plotly_chart(fig, use_container_width=True)



else:
    archivo = st.file_uploader("📄 Sube un .csv con columna 'color' (roja/verde)", type="csv")
    if archivo:
        df = pd.read_csv(archivo)
    else:
        df = pd.read_csv("data/velas_demo.csv")


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

# Mostrar resultados
st.subheader("📊 Resultados")
st.metric("Entradas totales", resultado['entradas'])
st.metric("Acertadas", resultado['aciertos'])
st.metric("Ciclos promedio", f"{resultado['prom_ciclos']:.2f}")
st.metric("Saldo final", f"${resultado['saldo_final']:.2f}")
st.metric("Drawdown máximo", f"{resultado['drawdown_max']:.2f}%")

st.line_chart(resultado['historial'])
