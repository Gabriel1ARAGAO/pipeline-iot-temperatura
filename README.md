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

## ▶️ Como Executar o Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/pipeline-iot-temperatura
cd pipeline-iot-temperatura
```

### 2. Instale as dependências
```bash
python -m venv venv
venv\Scripts\activate
pip install pandas psycopg2-binary sqlalchemy streamlit plotly
```

### 3. Suba o banco de dados PostgreSQL
```bash
docker run --name postgres-iot `
  -e POSTGRES_USER=iot_user `
  -e POSTGRES_PASSWORD=iot_senha `
  -e POSTGRES_DB=iot_db `
  -p 5432:5432 -d postgres
```

 Verifique se o container está rodando:
```bash
docker ps
```
> Deve aparecer `postgres-iot` com STATUS `Up`

 Caso não esteja rodando execute o comando abaixo:

>'docker start postgres-iot'

### 4. Execute o pipeline de dados
```bash
python src\pipeline.py
```
> Deve aparecer 'Pipeline concluído com sucesso!` no terminal

### 5. Abra o dashboard
```bash
streamlit run src\dashboard.py
```
> O navegador abrirá automaticamente em `http://localhost:8501`

---

## Ao Reiniciar o Computador

O container Docker para ao desligar a máquina.  
Antes de rodar o dashboard novamente, sempre execute:
```bash
docker start postgres-iot
```
```