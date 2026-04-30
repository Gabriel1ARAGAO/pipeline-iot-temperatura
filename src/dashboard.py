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
fig1 = px.bar(
    df_avg,
    x="device_id",
    y="avg_temp",
    color="avg_temp",
    color_continuous_scale="RdYlBu_r",
    text="avg_temp",
    labels={"device_id": "Dispositivo", "avg_temp": "Temp. Média (°C)"},
    title="Temperatura média registrada por sensor IoT"
)
fig1.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

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
    st.plotly_chart(fig2a, use_container_width=True)

with col_b:
    fig2b = px.bar(
        df_hora, x="hora", y="temp_media",
        color="temp_media",
        color_continuous_scale="thermal",
        labels={"hora": "Hora do Dia", "temp_media": "Temp. Média (°C)"},
        title="Temperatura média por hora do dia"
    )
    st.plotly_chart(fig2b, use_container_width=True)

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
st.plotly_chart(fig3, use_container_width=True)

st.caption("Fonte: Kaggle - Temperature Readings: IoT Devices | Desenvolvido com Python, PostgreSQL, Docker e Streamlit")