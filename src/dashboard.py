"""
Dashboard IoT - Visualização de Temperaturas
Execução: streamlit run src/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard IoT - Temperaturas",
    page_icon="🌡️",
    layout="wide"
)

# ─── CONEXÃO ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine(
        "postgresql://iot_user:iot_senha@localhost:5432/iot_db"
    )

@st.cache_data(ttl=60)
def load_view(view_name: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM {view_name}", engine)

# ─── CABEÇALHO ────────────────────────────────────────────────────────────────
st.title("🌡️ Dashboard de Temperaturas IoT")
st.markdown("Pipeline de dados com dispositivos IoT • PostgreSQL • Docker • Streamlit")
st.divider()

# ─── MÉTRICAS RÁPIDAS ─────────────────────────────────────────────────────────
engine = get_engine()
df_raw = pd.read_sql("SELECT temperature, device_id FROM temperature_readings LIMIT 50000", engine)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡️ Temp. Média Geral",  f"{df_raw['temperature'].mean():.1f} °C")
col2.metric("🔥 Temp. Máxima",       f"{df_raw['temperature'].max():.1f} °C")
col3.metric("❄️ Temp. Mínima",       f"{df_raw['temperature'].min():.1f} °C")
col4.metric("📡 Dispositivos",       df_raw['device_id'].nunique())

st.divider()

# ─── GRÁFICO 1: Média por Dispositivo ─────────────────────────────────────────
st.header("📡 Média de Temperatura por Dispositivo")
df_avg = load_view("avg_temp_por_dispositivo")

# Ordena do mais quente ao mais frio e cria labels
df_avg = df_avg.sort_values("avg_temp", ascending=False).reset_index(drop=True)
df_avg["sensor_label"] = ["Sensor " + str(i+1).zfill(3) for i in range(len(df_avg))]

# ── Controles interativos ──────────────────────────────────────────────────────
col_filtro1, col_filtro2 = st.columns(2)

with col_filtro1:
    top_n = st.slider(
        "Quantidade de dispositivos exibidos:",
        min_value=5,
        max_value=len(df_avg),
        value=15,
        step=5
    )

with col_filtro2:
    ordem = st.radio(
        "Ordenar por:",
        options=["Mais quentes primeiro", "Mais frios primeiro"],
        horizontal=True
    )

# ── Aplica filtros — sensores DIFERENTES por modo ─────────────────────────────
if ordem == "Mais quentes primeiro":
    # Pega os N sensores com MAIOR temperatura
    df_filtrado = df_avg.head(top_n).copy()
    escala_cor = "RdYlBu_r"   # vermelho = quente
else:
    # Pega os N sensores com MENOR temperatura (completamente diferentes!)
    df_filtrado = df_avg.tail(top_n).sort_values("avg_temp").copy()
    escala_cor = "RdYlBu"     # azul = frio

# ── Escala de cor dinâmica — usa o range dos dados filtrados ──────────────────
temp_min = df_filtrado["avg_temp"].min()
temp_max = df_filtrado["avg_temp"].max()

# Amplia o range para forçar maior contraste visual entre as barras
margem = (temp_max - temp_min) * 0.1   # 10% de margem
range_cor = [temp_min - margem, temp_max + margem]

# ── Gráfico ────────────────────────────────────────────────────────────────────
fig1 = px.bar(
    df_filtrado,
    x="sensor_label",
    y="avg_temp",
    color="avg_temp",
    color_continuous_scale=escala_cor,
    range_color=range_cor,          # ← força escala de cor local
    text="avg_temp",
    labels={"sensor_label": "Dispositivo", "avg_temp": "Temp. Média (°C)"},
    title="Temperatura Média",
    hover_data={"device_id": True}
)
fig1.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
fig1.update_layout(
    xaxis_tickangle=-45,
    coloraxis_colorbar=dict(title="Temp. (°C)")
)
st.plotly_chart(fig1, width='stretch')
# ─── GRÁFICO 2: Leituras por Hora ─────────────────────────────────────────────
st.header("⏰ Padrão de Leituras ao Longo do Dia")
df_hora = load_view("leituras_por_hora")
col_a, col_b = st.columns(2)

with col_a:
    fig2a = px.line(
        df_hora, x="hora", y="contagem",
        markers=True,
        labels={"hora": "Hora do Dia", "contagem": "Nº de Leituras"},
        title="Volume de leituras por hora"
    )
    st.plotly_chart(fig2a, width='stretch')

with col_b:
    fig2b = px.bar(
        df_hora, x="hora", y="temp_media",
        color="temp_media",
        color_continuous_scale="thermal",
        labels={"hora": "Hora do Dia", "temp_media": "Temp. Média (°C)"},
        title="Temperatura média por hora do dia"
    )
    st.plotly_chart(fig2b, width='stretch')

# ─── GRÁFICO 3: Máximas e Mínimas por Dia ────────────────────────────────────
st.header("📅 Variação Diária de Temperatura")
df_dia = load_view("temp_max_min_por_dia")
fig3 = px.line(
    df_dia, x="data",
    y=["temp_max", "temp_min", "temp_media"],
    labels={"data": "Data", "value": "Temperatura (°C)", "variable": "Indicador"},
    title="Temperaturas máxima, mínima e média por dia",
    color_discrete_map={
        "temp_max":   "#FF4B4B",
        "temp_min":   "#4B7BFF",
        "temp_media": "#FFA500"
    }
)
fig3.update_layout(hovermode="x unified")
st.plotly_chart(fig3, width='stretch')

st.caption("Fonte: Kaggle - Temperature Readings: IoT Devices | Desenvolvido com Python, PostgreSQL, Docker e Streamlit")
