#  Pipeline de Dados IoT — Temperatura com Docker e Streamlit

##  Sobre o Projeto
Pipeline completo que ingere leituras de temperatura de sensores IoT,
armazena no PostgreSQL (via Docker) e exibe visualizações interativas
com Streamlit.

**Tecnologias:** Python · PostgreSQL · Docker · SQLAlchemy · Streamlit · Plotly

## Estrutura

pipeline-iot-temperatura/
├── src/
│   ├── pipeline.py    # Ingestão e limpeza dos dados
│   ├── dashboard.py   # Dashboard interativo
│   └── views.sql      # Views SQL documentadas
├── data/              # CSV do Kaggle (não incluído no repo)
├── docs/screenshots/  # Prints do dashboard
└── README.md

##Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/pipeline-iot-temperatura
cd pipeline-iot-temperatura
```

### 2. Suba o PostgreSQL
```bash
docker run --name postgres-iot \
  -e POSTGRES_USER=iot_user \
  -e POSTGRES_PASSWORD=iot_senha \
  -e POSTGRES_DB=iot_db \
  -p 5432:5432 -d postgres
```

### 3. Instale dependências
```bash
python -m venv venv && source venv/bin/activate
pip install pandas psycopg2-binary sqlalchemy streamlit plotly
```

### 4. Baixe o dataset
Acesse: https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices
Salve o CSV em `data/temperatures.csv`

### 5. Execute o pipeline
```bash
python src/pipeline.py
```

### 6. Execute o dashboard
```bash
streamlit run src/dashboard.py
```