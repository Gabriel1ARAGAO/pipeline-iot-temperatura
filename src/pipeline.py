"""
Pipeline de Dados IoT - Temperatura
Lê o CSV do Kaggle e insere no PostgreSQL
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
DB_USER     = "iot_user"
DB_PASSWORD = "iot_senha"
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "iot_db"

CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/temperatures.csv")

# ─── CONEXÃO COM O BANCO ──────────────────────────────────────────────────────
def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

# ─── LEITURA E LIMPEZA DOS DADOS ─────────────────────────────────────────────
def load_and_clean_csv(path: str) -> pd.DataFrame:
    print(f"📂 Lendo arquivo: {path}")
    df = pd.read_csv(path)

    print(f"   Colunas encontradas: {df.columns.tolist()}")
    print(f"   Total de linhas: {len(df)}")

    # Padroniza nomes de colunas (minúsculas, sem espaços)
    df.columns = [c.strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]

    # Renomeia para nomes padronizados
    df = df.rename(columns={
        "noted_date": "reading_time",
        "temp":       "temperature",
        "out_in":     "location_type",
        "id":         "device_id"
    })

    # Converte a coluna de data/hora
    df["reading_time"] = pd.to_datetime(df["reading_time"], dayfirst=True, errors="coerce")

    # Remove linhas com dados nulos essenciais
    df = df.dropna(subset=["reading_time", "temperature"])

    # Garante que temperatura é numérica
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df = df.dropna(subset=["temperature"])

    print(f"   Linhas após limpeza: {len(df)}")
    return df

# ─── CRIAÇÃO DA TABELA ────────────────────────────────────────────────────────
def create_table(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS temperature_readings (
                id            SERIAL PRIMARY KEY,
                device_id     VARCHAR(50),
                reading_time  TIMESTAMP,
                temperature   FLOAT,
                location_type VARCHAR(10)
            );
        """))
        conn.commit()
    print("✅ Tabela 'temperature_readings' criada/verificada.")

# ─── CRIAÇÃO DAS VIEWS SQL ────────────────────────────────────────────────────
def create_views(engine):
    views = {

        "avg_temp_por_dispositivo": """
            CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
            SELECT
                device_id,
                ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
                COUNT(*) AS total_leituras
            FROM temperature_readings
            GROUP BY device_id
            ORDER BY avg_temp DESC;
        """,

        "leituras_por_hora": """
            CREATE OR REPLACE VIEW leituras_por_hora AS
            SELECT
                EXTRACT(HOUR FROM reading_time) AS hora,
                COUNT(*) AS contagem,
                ROUND(AVG(temperature)::numeric, 2) AS temp_media
            FROM temperature_readings
            GROUP BY hora
            ORDER BY hora;
        """,

        "temp_max_min_por_dia": """
            CREATE OR REPLACE VIEW temp_max_min_por_dia AS
            SELECT
                DATE(reading_time) AS data,
                MAX(temperature)   AS temp_max,
                MIN(temperature)   AS temp_min,
                ROUND(AVG(temperature)::numeric, 2) AS temp_media
            FROM temperature_readings
            GROUP BY DATE(reading_time)
            ORDER BY data;
        """
    }

    with engine.connect() as conn:
        for name, sql in views.items():
            conn.execute(text(sql))
            conn.commit()
            print(f"✅ View '{name}' criada.")

# ─── INSERÇÃO DOS DADOS ───────────────────────────────────────────────────────
def insert_data(df: pd.DataFrame, engine):
    df.to_sql(
        "temperature_readings",
        engine,
        if_exists="replace",   # troca por "append" se quiser acumular
        index=False,
        chunksize=1000
    )
    print(f"✅ {len(df)} registros inseridos na tabela!")

# ─── EXECUÇÃO PRINCIPAL ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Iniciando Pipeline IoT")
    print("=" * 50)

    engine = get_engine()
    df     = load_and_clean_csv(CSV_PATH)

    create_table(engine)
    insert_data(df, engine)
    create_views(engine)

    print("\n🎉 Pipeline concluído com sucesso!")