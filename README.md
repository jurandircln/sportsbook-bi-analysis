# Sportsbook BI Analysis

Sistema de análise de dados da temporada de futebol romeno 2018/19.
Entrega respostas sobre performance, comportamento de clientes e preferências de apostas
— não apenas dashboards.

## O que o sistema entrega

- **Pipeline de dados** — CSV → bronze → silver (star schema) → gold usando PostgreSQL + Docker
- **Dashboard interativo** — análise exploratória da temporada por segmento, CRM level,
  canal e período (Streamlit + Plotly)
- **Agente de BI** — responde perguntas de negócio sobre a temporada em linguagem natural
  (Agno + Claude)

## Arquitetura

```
data/raw/*.csv
      │
      ▼
┌─────────────┐
│   BRONZE    │  src/ingestion/
│ (PostgreSQL)│  Ingestão direta dos CSVs, sem transformação
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   SILVER    │  src/transformation/silver/
│ (Star Schema│  Limpeza, tipagem, Star Schema (fato + dimensão)
│  PostgreSQL)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    GOLD     │  src/transformation/gold/
│ (PostgreSQL)│  Métricas agregadas por cliente, segmento e CRM level
└──────┬──────┘
       │
       ├──────────────────────┐
       ▼                      ▼
┌─────────────┐      ┌──────────────────┐
│  DASHBOARD  │      │     AGENTE       │
│  Streamlit  │      │  Agno + Claude   │
│  :8501      │      │  (aba no painel) │
└─────────────┘      └──────────────────┘
```

## As perguntas de negócio que o sistema responde

**P1 — Como foi a performance geral da temporada?**
Gross Revenue, Turnover e Margem mês a mês. Evolução da base de clientes ativos.

**P2 — Como se comportou a base de clientes?**
Segmentação em novos, existentes e saindo. Volume e receita por segmento ao longo da temporada.

**P3 — Quais são as preferências dos apostadores?**
Live vs. Pre-event, canal preferido (Android/iOS/Web), mercados mais apostados
e horários de pico de atividade.

**P4 — Como performa cada CRM Level?**
Gross Revenue, Turnover e número de apostas por nível. Quais níveis geram mais valor.

**P5 — Como foi a adoção do Cash Out?**
Taxa de adoção, taxa de sucesso e valor médio por tentativa. Evolução mês a mês
(funcionalidade nova na temporada).

Use o agente para fazer estas perguntas diretamente em linguagem natural.

## Como rodar

### Docker (recomendado)

Pré-requisito: Docker Desktop instalado e `ANTHROPIC_API_KEY` disponível.

```bash
# Clone o repositório
git clone https://github.com/jurandircln/sportsbook-bi-analysis.git
cd sportsbook-bi-analysis

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua ANTHROPIC_API_KEY

# Copie os CSVs para data/raw/
# (Cashouts.csv, Customer.csv, Customer_crm_level.csv, Events.csv, Sportsbook.csv)

# Suba o ambiente
docker compose up -d
```

Dashboard disponível em: **http://localhost:8501**

### Local (uv)

Pré-requisito: uv instalado e Python 3.12+.

```bash
git clone https://github.com/jurandircln/sportsbook-bi-analysis.git
cd sportsbook-bi-analysis

uv sync
cp .env.example .env   # edite com sua ANTHROPIC_API_KEY

# Suba o PostgreSQL
docker compose up postgres -d

# Execute o pipeline
uv run python src/ingestion/run_ingestion.py
uv run python src/transformation/run_silver.py
uv run python src/transformation/run_gold.py

# Suba o dashboard
uv run streamlit run src/dashboard/app.py
```

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
|---|---|---|
| ANTHROPIC_API_KEY | Sim | Chave da API Anthropic para o agente de IA |
| POSTGRES_USER | Sim | Usuário do PostgreSQL |
| POSTGRES_PASSWORD | Sim | Senha do PostgreSQL |
| POSTGRES_DB | Sim | Nome do banco de dados |
| DATABASE_URL | Sim | URL de conexão completa |

Ver `.env.example` para valores padrão.

## Estrutura do projeto

```
sportsbook-bi-analysis/
├── CLAUDE.md                    # Guia de desenvolvimento com IA (SDD)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml               # Dependências (uv)
├── data/
│   └── raw/                     # CSVs originais — não versionados
├── sql/
│   ├── bronze/                  # DDLs da camada Bronze
│   ├── silver/                  # DDLs Star Schema (fact_* + dim_*)
│   └── gold/                    # DDLs das métricas analíticas
├── src/
│   ├── ingestion/               # CSV → Bronze
│   ├── transformation/          # Bronze → Silver → Gold
│   ├── agent/                   # Agente Agno + SQL tools
│   └── dashboard/               # Aplicação Streamlit
├── docs/
│   ├── business-context/        # Visão, personas, jornadas, KPIs
│   ├── product-context/         # Regras de negócio, glossário
│   └── technical-context/       # Stack, ADRs, catálogo de dados
└── tests/
```

## Stack

| Tecnologia | Versão | Papel |
|---|---|---|
| Python | 3.12+ | Runtime |
| PostgreSQL | 16 | Banco de dados (schemas bronze/silver/gold) |
| Docker + Compose | latest | Ambiente reproduzível |
| Streamlit | ≥1.32 | Dashboard interativo |
| Plotly | ≥5.20 | Visualizações |
| Agno | ≥1.4 | Framework de agentes de IA |
| Claude (Anthropic) | claude-sonnet-4-6 | LLM do agente |
| uv | latest | Gerenciamento de dependências |
