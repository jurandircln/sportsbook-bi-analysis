# Sportsbook BI Analysis — Plano de Implementação: Estrutura Base

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a estrutura base completa do projeto seguindo SDD — repositório, modelagem de banco (DDLs das 3 camadas), CLAUDE.md, documentação de contexto, skills, ADRs, catálogo de dados, Docker e primeira versão no GitHub.

**Architecture:** Projeto Python 3.12 com uv, PostgreSQL 16 em Docker com arquitetura medalhão (Bronze/Silver/Gold), dashboard Streamlit + agente Agno/Claude a ser implementado no plano seguinte. Toda documentação segue a metodologia SDD com 3 camadas de contexto.

**Tech Stack:** Python 3.12, uv, PostgreSQL 16, Docker Compose, Streamlit, Agno, Anthropic Claude, Git/GitHub

> **Este é o Plano 1 de 2.** O Plano 2 cobrirá ingestão de dados, transformações Silver/Gold, dashboard Streamlit e agente Agno.

---

## Mapeamento de Arquivos

```
sportsbook-bi-analysis/
├── .claude/skills/
│   ├── db-modeling.md
│   ├── create-adr.md
│   ├── update-business-rules.md
│   └── update-data-catalog.md
├── .cursor/rules/
│   └── global.mdc
├── data/raw/.gitkeep
├── docker/
│   └── init.sql                          ← script de inicialização do banco
├── docs/
│   ├── business-context/
│   │   ├── vision.md
│   │   ├── personas.md
│   │   ├── journeys.md
│   │   ├── competitive.md
│   │   ├── kpis.md
│   │   └── features/.gitkeep
│   ├── product-context/
│   │   ├── features/.gitkeep
│   │   ├── business-rules.md
│   │   └── glossary.md
│   ├── technical-context/
│   │   ├── stack.md
│   │   ├── codebase-guide.md
│   │   ├── data-catalog/
│   │   │   ├── overview.md
│   │   │   ├── bronze/
│   │   │   │   ├── cashouts.md
│   │   │   │   ├── customer.md
│   │   │   │   ├── customer_crm_level.md
│   │   │   │   ├── events.md
│   │   │   │   └── sportsbook.md
│   │   │   ├── silver/README.md
│   │   │   └── gold/README.md
│   │   └── adr/
│   │       ├── ADR-001-medallion-architecture.md
│   │       ├── ADR-002-database-modeling.md
│   │       ├── ADR-003-agno-agent-design.md
│   │       ├── ADR-004-stack-and-tooling.md
│   │       └── ADR-005-data-catalog.md
│   └── superpowers/
│       ├── specs/2026-04-26-sportsbook-bi-analysis-design.md
│       └── plans/2026-04-26-base-structure.md
├── sql/
│   ├── bronze/
│   │   ├── 001_create_schema.sql
│   │   ├── 002_create_cashouts.sql
│   │   ├── 003_create_customer.sql
│   │   ├── 004_create_customer_crm_level.sql
│   │   ├── 005_create_events.sql
│   │   └── 006_create_sportsbook.sql
│   ├── silver/
│   │   ├── 001_create_schema.sql
│   │   ├── 002_create_customer.sql
│   │   ├── 003_create_customer_crm_level.sql
│   │   ├── 004_create_events.sql
│   │   ├── 005_create_sportsbook.sql
│   │   └── 006_create_cashouts.sql
│   └── gold/
│       ├── 001_create_schema.sql
│       ├── 002_create_customer_performance.sql
│       ├── 003_create_customer_segments.sql
│       ├── 004_create_betting_preferences.sql
│       ├── 005_create_crm_performance.sql
│       ├── 006_create_season_summary.sql
│       └── 007_create_cashout_analysis.sql
├── src/
│   ├── ingestion/__init__.py
│   ├── transformation/__init__.py
│   ├── agent/__init__.py
│   └── dashboard/__init__.py
├── tests/.gitkeep
├── .env.example
├── .gitignore
├── CLAUDE.md
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Task 1: Inicializar repositório Git e criar repositório no GitHub

**Files:**
- Create: `README.md` (temporário para init do GitHub)

- [ ] **Step 1: Criar o repositório no GitHub via CLI**

```bash
cd /Users/jurandirneto/Documents/Pessoal/Estudos/Kaizen/study-case
git init
echo "# sportsbook-bi-analysis" > README.md
git add README.md
git commit -m "chore: initial commit"
gh repo create jurandircln/sportsbook-bi-analysis --public --source=. --remote=origin --push
```

Saída esperada: repositório criado em `https://github.com/jurandircln/sportsbook-bi-analysis`

---

## Task 2: Criar estrutura de diretórios e arquivos raiz

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: múltiplos diretórios com `.gitkeep`

- [ ] **Step 1: Criar todos os diretórios do projeto**

```bash
mkdir -p .claude/skills
mkdir -p .cursor/rules
mkdir -p data/raw
mkdir -p docker
mkdir -p docs/business-context/features
mkdir -p docs/product-context/features
mkdir -p docs/technical-context/data-catalog/bronze
mkdir -p docs/technical-context/data-catalog/silver
mkdir -p docs/technical-context/data-catalog/gold
mkdir -p docs/technical-context/adr
mkdir -p docs/superpowers/specs
mkdir -p docs/superpowers/plans
mkdir -p sql/bronze
mkdir -p sql/silver
mkdir -p sql/gold
mkdir -p src/ingestion
mkdir -p src/transformation
mkdir -p src/agent
mkdir -p src/dashboard
mkdir -p tests
```

- [ ] **Step 2: Criar arquivos `.gitkeep` para manter diretórios vazios no Git**

```bash
touch data/raw/.gitkeep
touch docs/business-context/features/.gitkeep
touch docs/product-context/features/.gitkeep
touch tests/.gitkeep
```

- [ ] **Step 3: Criar `.gitignore`**

```
# Variáveis de ambiente
.env

# Dados brutos (não versionar CSVs)
data/raw/*.csv
data/raw/*.CSV

# Python
__pycache__/
*.py[cod]
*.pyo
.Python
.venv/
venv/
.uv/
*.egg-info/
dist/
build/
.eggs/

# uv
uv.lock

# Jupyter
.ipynb_checkpoints/
*.ipynb

# IDEs
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Docker
.docker/

# Logs
*.log
logs/

# Coverage
.coverage
htmlcov/
.pytest_cache/
```

- [ ] **Step 4: Criar `.env.example`**

```bash
# =====================================================
# Variáveis de ambiente do projeto Sportsbook BI Analysis
# Copie este arquivo para .env e preencha os valores
# =====================================================

# --- Anthropic (Claude) ---
ANTHROPIC_API_KEY=sk-ant-...

# --- PostgreSQL ---
POSTGRES_USER=sportsbook
POSTGRES_PASSWORD=sportsbook123
POSTGRES_DB=sportsbook_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# --- URL de conexão completa (usada pela aplicação) ---
DATABASE_URL=postgresql://sportsbook:sportsbook123@postgres:5432/sportsbook_db

# --- Streamlit ---
STREAMLIT_PORT=8501
```

- [ ] **Step 5: Criar `__init__.py` nos módulos Python**

```bash
touch src/ingestion/__init__.py
touch src/transformation/__init__.py
touch src/agent/__init__.py
touch src/dashboard/__init__.py
```

- [ ] **Step 6: Criar stub mínimo do dashboard para o Dockerfile não falhar**

```python
# src/dashboard/app.py
# Placeholder do dashboard — será implementado no Plano 2
import streamlit as st

st.title("Sportsbook BI Analysis")
st.info("Dashboard em construção. Execute o Plano 2 para implementar as análises.")
```

- [ ] **Step 6: Commit**

```bash
git add .gitignore .env.example data/ src/ tests/
git commit -m "chore: criar estrutura de diretórios e arquivos raiz"
```

---

## Task 3: Configurar pyproject.toml e dependências Python

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Criar `pyproject.toml`**

```toml
[project]
name = "sportsbook-bi-analysis"
version = "0.1.0"
description = "Análise de dados da temporada de futebol romeno 2018/19 — Sportsbook Product Team"
requires-python = ">=3.12"
dependencies = [
    # Interface web
    "streamlit>=1.32.0",
    # Framework de agentes de IA
    "agno>=1.4.0",
    # SDK da Anthropic (Claude)
    "anthropic>=0.25.0",
    # Banco de dados
    "psycopg2-binary>=2.9.0",
    "sqlalchemy>=2.0.0",
    # Manipulação de dados
    "pandas>=2.2.0",
    # Variáveis de ambiente
    "python-dotenv>=1.0.0",
    # Visualizações
    "plotly>=5.20.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

- [ ] **Step 2: Inicializar o ambiente uv**

```bash
uv sync
```

Saída esperada: dependências instaladas em `.venv/`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: configurar pyproject.toml com dependências Python via uv"
```

---

## Task 4: Criar ADR-002 — Modelagem do Banco de Dados (modelagem antes do código)

**Files:**
- Create: `docs/technical-context/adr/ADR-002-database-modeling.md`

> A modelagem é o início do projeto. O ADR-002 documenta as decisões de schema antes de escrever qualquer DDL.

- [ ] **Step 1: Criar `docs/technical-context/adr/ADR-002-database-modeling.md`**

```markdown
# ADR-002: Modelagem Inicial do Banco de Dados

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

O projeto analisa 5 fontes de dados CSV da temporada de futebol romeno 2018/19:
Cashouts, Customer, Customer_crm_level, Events e Sportsbook. Precisávamos definir
como modelar essas fontes em um banco relacional organizado em 3 camadas (medalhão),
com decisões claras sobre tipos de dados, granularidade e relações.

## Decisão

### Camada Bronze
Todas as colunas recebem tipo TEXT na Bronze, preservando exatamente o dado original
do CSV sem risco de perda por cast incorreto. Cada tabela recebe coluna `ingested_at`
(TIMESTAMP) para rastreabilidade da ingestão.

Tabelas: `bronze.cashouts`, `bronze.customer`, `bronze.customer_crm_level`,
`bronze.events`, `bronze.sportsbook`

### Camada Silver
Dados tipados corretamente e com regras de negócio aplicadas:
- `customer_id` e `event_id`: INTEGER (IDs numéricos)
- Datas: DATE para datas sem hora, TIMESTAMP para timestamps
- Valores monetários: NUMERIC(12,2) para evitar arredondamentos de float
- `is_live` (BOOLEAN): calculado como `placed_at >= event_start_time`
- `gross_revenue` (NUMERIC): calculado como `turnover - winnings`
- `crm_level` na tabela silver.customer_crm_level: preenchimento forward-fill
  para meses sem registro (usa nível mais recente atribuído)

Cada tabela Silver mantém `ingested_at` herdado do Bronze para rastreabilidade.

### Camada Gold
Tabelas analíticas desnormalizadas prontas para consumo direto pelo dashboard
e pelo agente de BI. Preferimos tabelas materializadas a views para garantir
performance em queries do Streamlit e do agente.

Tabelas: `gold.customer_performance`, `gold.customer_segments`,
`gold.betting_preferences`, `gold.crm_performance`, `gold.season_summary`,
`gold.cashout_analysis`

### Definição de segmentos de clientes
- **Novo**: primeira aposta realizada durante a temporada (Set/2018–Ago/2019)
- **Existente**: apostas antes E durante a temporada
- **Saindo**: apostas antes da temporada, mas sem apostas nos últimos 3 meses dela

### Definição Live vs. Pre-event
- **Live**: `SportBetSettled_Placed >= Event_Start_Time`
- **Pre-event**: `SportBetSettled_Placed < Event_Start_Time`

## Consequências

O uso de TEXT na Bronze torna a ingestão mais robusta (nenhum CSV mal formatado
causa erro de tipo). A Silver aplica os casts com tratamento explícito, tornando
erros de dados visíveis. A Gold desnormaliza para performance de leitura, aceitando
redundância controlada de dados.
```

- [ ] **Step 2: Commit**

```bash
git add docs/technical-context/adr/ADR-002-database-modeling.md
git commit -m "docs: adicionar ADR-002 com decisões de modelagem do banco"
```

---

## Task 5: Criar DDLs da Camada Bronze

**Files:**
- Create: `sql/bronze/001_create_schema.sql`
- Create: `sql/bronze/002_create_cashouts.sql`
- Create: `sql/bronze/003_create_customer.sql`
- Create: `sql/bronze/004_create_customer_crm_level.sql`
- Create: `sql/bronze/005_create_events.sql`
- Create: `sql/bronze/006_create_sportsbook.sql`

- [ ] **Step 1: Criar `sql/bronze/001_create_schema.sql`**

```sql
-- Cria o schema da camada Bronze
-- Bronze: dados brutos ingeridos diretamente dos CSVs, sem transformação
CREATE SCHEMA IF NOT EXISTS bronze;
```

- [ ] **Step 2: Criar `sql/bronze/002_create_cashouts.sql`**

```sql
-- Tabela Bronze: tentativas de cash out
-- Fonte: Cashouts.csv
-- Todas as colunas em TEXT para preservar dado original sem risco de cast
CREATE TABLE IF NOT EXISTS bronze.cashouts (
    cashout_attempt_bet_id          TEXT,           -- ID da aposta
    cashout_attempt_bet_cashout_id  TEXT,           -- ID da tentativa de cash out
    cashout_attempt_bet_cashout_created TEXT,       -- timestamp da tentativa (raw)
    cashout_attempt_bet_cashout_status  TEXT,       -- status da tentativa
    cashout_attempt_cashout_amount      TEXT,       -- valor do cash out (raw)
    ingested_at                         TIMESTAMP DEFAULT NOW()  -- controle de ingestão
);
```

- [ ] **Step 3: Criar `sql/bronze/003_create_customer.sql`**

```sql
-- Tabela Bronze: base de clientes
-- Fonte: Customer.csv
CREATE TABLE IF NOT EXISTS bronze.customer (
    customer_id              TEXT,   -- ID único do cliente
    customer_datecreation_id TEXT,   -- data de cadastro (raw)
    customer_gender_name     TEXT,   -- gênero do cliente
    customer_birthday        TEXT,   -- data de nascimento (raw)
    ingested_at              TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 4: Criar `sql/bronze/004_create_customer_crm_level.sql`**

```sql
-- Tabela Bronze: níveis CRM mensais por cliente
-- Fonte: Customer_crm_level.csv
-- ATENÇÃO: registros existem apenas nos meses de mudança de nível.
-- Para meses intermediários, aplicar forward-fill na camada Silver.
CREATE TABLE IF NOT EXISTS bronze.customer_crm_level (
    customer_id    TEXT,   -- ID único do cliente
    date_yearmonth TEXT,   -- mês de atribuição do nível (ex: "2018-10")
    crm_level      TEXT,   -- nível CRM atribuído (ex: Bronze, Silver, Gold)
    ingested_at    TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 5: Criar `sql/bronze/005_create_events.sql`**

```sql
-- Tabela Bronze: informações de eventos esportivos
-- Fonte: Events.csv
CREATE TABLE IF NOT EXISTS bronze.events (
    event_id         TEXT,   -- ID único do evento
    event_sport_name TEXT,   -- tipo de esporte
    event_class_name TEXT,   -- classe do evento
    event_type_name  TEXT,   -- tipo de liga
    event_name       TEXT,   -- nome do evento
    event_start_time TEXT,   -- horário real de início (raw)
    event_end_time   TEXT,   -- horário real de término (raw)
    ingested_at      TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 6: Criar `sql/bronze/006_create_sportsbook.sql`**

```sql
-- Tabela Bronze: atividade de apostas
-- Fonte: Sportsbook.csv
-- KPI principal: Gross Revenue = Turnover - Winnings (calculado na Silver)
CREATE TABLE IF NOT EXISTS bronze.sportsbook (
    sportbetsettled_bet_id      TEXT,   -- ID da aposta
    bettype_name                TEXT,   -- tipo de aposta
    market_template_name        TEXT,   -- mercado da aposta
    sportbetsettled_customer_id TEXT,   -- ID do cliente
    sportbetsettled_settled     TEXT,   -- timestamp de liquidação da aposta (raw)
    sportbetsettled_placed      TEXT,   -- timestamp de colocação da aposta (raw)
    channel_name                TEXT,   -- dispositivo usado (Android, iOS, etc.)
    sportbetsettled_event_id    TEXT,   -- ID do evento
    turnover                    TEXT,   -- valor apostado (raw)
    winnings                    TEXT,   -- ganhos do cliente (raw)
    ingested_at                 TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 7: Commit**

```bash
git add sql/bronze/
git commit -m "feat: adicionar DDLs da camada Bronze"
```

---

## Task 6: Criar DDLs da Camada Silver

**Files:**
- Create: `sql/silver/001_create_schema.sql`
- Create: `sql/silver/002_create_customer.sql`
- Create: `sql/silver/003_create_customer_crm_level.sql`
- Create: `sql/silver/004_create_events.sql`
- Create: `sql/silver/005_create_sportsbook.sql`
- Create: `sql/silver/006_create_cashouts.sql`

- [ ] **Step 1: Criar `sql/silver/001_create_schema.sql`**

```sql
-- Cria o schema da camada Silver
-- Silver: dados limpos, tipados e com regras de negócio aplicadas
CREATE SCHEMA IF NOT EXISTS silver;
```

- [ ] **Step 2: Criar `sql/silver/002_create_customer.sql`**

```sql
-- Tabela Silver: clientes com tipos corretos e idade calculada
-- Fonte: bronze.customer
CREATE TABLE IF NOT EXISTS silver.customer (
    customer_id        INTEGER PRIMARY KEY,  -- ID numérico do cliente
    registration_date  DATE NOT NULL,        -- data de cadastro
    gender             VARCHAR(20),          -- gênero
    birth_date         DATE,                 -- data de nascimento
    age                INTEGER,              -- idade calculada no momento da análise
    ingested_at        TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 3: Criar `sql/silver/003_create_customer_crm_level.sql`**

```sql
-- Tabela Silver: níveis CRM mensais com forward-fill aplicado
-- Regra de negócio: para meses sem registro, usar o nível mais recente atribuído.
-- Exemplo: Bronze em Out/18 e Silver em Jan/19 → Nov e Dez/18 são Bronze.
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.customer_crm_level (
    customer_id  INTEGER  NOT NULL,          -- ID do cliente
    year_month   DATE     NOT NULL,          -- primeiro dia do mês (ex: 2018-10-01)
    crm_level    VARCHAR(50) NOT NULL,       -- nível CRM após forward-fill
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);
```

- [ ] **Step 4: Criar `sql/silver/004_create_events.sql`**

```sql
-- Tabela Silver: eventos com tipos corretos
-- Fonte: bronze.events
CREATE TABLE IF NOT EXISTS silver.events (
    event_id    INTEGER PRIMARY KEY,    -- ID numérico do evento
    sport_name  VARCHAR(100),           -- tipo de esporte
    class_name  VARCHAR(100),           -- classe do evento
    type_name   VARCHAR(100),           -- tipo de liga
    event_name  VARCHAR(255),           -- nome do evento
    start_time  TIMESTAMP,              -- horário de início
    end_time    TIMESTAMP,              -- horário de término
    ingested_at TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 5: Criar `sql/silver/005_create_sportsbook.sql`**

```sql
-- Tabela Silver: apostas com tipos corretos, gross revenue e flag live
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (aposta feita após início do evento)
-- Fonte: bronze.sportsbook + silver.events (para event_start_time)
CREATE TABLE IF NOT EXISTS silver.sportsbook (
    bet_id         TEXT         PRIMARY KEY,    -- ID da aposta
    bet_type       VARCHAR(100),                -- tipo de aposta
    market         VARCHAR(100),                -- mercado
    customer_id    INTEGER      NOT NULL,       -- ID do cliente
    settled_at     TIMESTAMP,                   -- quando a aposta foi liquidada
    placed_at      TIMESTAMP    NOT NULL,       -- quando a aposta foi feita
    channel        VARCHAR(50),                 -- dispositivo (Android, iOS, Web, etc.)
    event_id       INTEGER,                     -- ID do evento
    turnover       NUMERIC(12,2) NOT NULL,      -- valor apostado
    winnings       NUMERIC(12,2) NOT NULL,      -- ganhos do cliente
    gross_revenue  NUMERIC(12,2) NOT NULL,      -- receita bruta = turnover - winnings
    is_live        BOOLEAN       NOT NULL,      -- TRUE se aposta feita após início do evento
    ingested_at    TIMESTAMP DEFAULT NOW()
);

-- Índices para queries analíticas frequentes
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_customer
    ON silver.sportsbook (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_placed_at
    ON silver.sportsbook (placed_at);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_event
    ON silver.sportsbook (event_id);
```

- [ ] **Step 6: Criar `sql/silver/006_create_cashouts.sql`**

```sql
-- Tabela Silver: tentativas de cash out com tipos corretos
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.cashouts (
    bet_id          TEXT         NOT NULL,   -- ID da aposta relacionada
    cashout_id      TEXT         PRIMARY KEY, -- ID da tentativa de cash out
    created_at      TIMESTAMP    NOT NULL,   -- quando a tentativa foi feita
    status          VARCHAR(50)  NOT NULL,   -- status (ex: Success, Failed)
    cashout_amount  NUMERIC(12,2),           -- valor do cash out
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_cashouts_bet
    ON silver.cashouts (bet_id);
```

- [ ] **Step 7: Commit**

```bash
git add sql/silver/
git commit -m "feat: adicionar DDLs da camada Silver com regras de negócio documentadas"
```

---

## Task 7: Criar DDLs da Camada Gold

**Files:**
- Create: `sql/gold/001_create_schema.sql`
- Create: `sql/gold/002_create_customer_performance.sql`
- Create: `sql/gold/003_create_customer_segments.sql`
- Create: `sql/gold/004_create_betting_preferences.sql`
- Create: `sql/gold/005_create_crm_performance.sql`
- Create: `sql/gold/006_create_season_summary.sql`
- Create: `sql/gold/007_create_cashout_analysis.sql`

- [ ] **Step 1: Criar `sql/gold/001_create_schema.sql`**

```sql
-- Cria o schema da camada Gold
-- Gold: tabelas analíticas desnormalizadas, prontas para consumo pelo dashboard e agente
CREATE SCHEMA IF NOT EXISTS gold;
```

- [ ] **Step 2: Criar `sql/gold/002_create_customer_performance.sql`**

```sql
-- Tabela Gold: KPIs de performance por cliente na temporada
-- Consumida por: dashboard (visão de clientes), agente (perguntas de performance)
CREATE TABLE IF NOT EXISTS gold.customer_performance (
    customer_id          INTEGER PRIMARY KEY,   -- ID do cliente
    gender               VARCHAR(20),           -- gênero
    age                  INTEGER,               -- idade no momento da análise
    total_bets           INTEGER,               -- total de apostas na temporada
    total_turnover       NUMERIC(12,2),         -- soma do valor apostado
    total_winnings       NUMERIC(12,2),         -- soma dos ganhos do cliente
    gross_revenue        NUMERIC(12,2),         -- receita bruta total (turnover - winnings)
    live_bets            INTEGER,               -- apostas feitas ao vivo
    pre_event_bets       INTEGER,               -- apostas pré-evento
    cashout_attempts     INTEGER,               -- tentativas de cash out
    successful_cashouts  INTEGER,               -- cash outs com sucesso
    updated_at           TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 3: Criar `sql/gold/003_create_customer_segments.sql`**

```sql
-- Tabela Gold: segmentação dos clientes na temporada
-- Segmentos:
--   novo       = primeira aposta ocorreu durante a temporada (Set/2018–Ago/2019)
--   existente  = apostas antes E durante a temporada
--   saindo     = apostas antes da temporada, sem apostas nos últimos 3 meses dela
-- Consumida por: dashboard (comportamento da base), agente (perguntas de segmentação)
CREATE TABLE IF NOT EXISTS gold.customer_segments (
    customer_id     INTEGER PRIMARY KEY,   -- ID do cliente
    segment         VARCHAR(20) NOT NULL,  -- 'novo', 'existente', 'saindo'
    first_bet_date  DATE,                  -- data da primeira aposta (histórico completo)
    last_bet_date   DATE,                  -- data da última aposta na temporada
    crm_level       VARCHAR(50),           -- nível CRM predominante na temporada
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 4: Criar `sql/gold/004_create_betting_preferences.sql`**

```sql
-- Tabela Gold: preferências de aposta por cliente
-- Consumida por: dashboard (preferências), agente (perguntas de comportamento)
CREATE TABLE IF NOT EXISTS gold.betting_preferences (
    customer_id          INTEGER PRIMARY KEY,  -- ID do cliente
    preferred_channel    VARCHAR(50),          -- canal com mais apostas (ex: Android, iOS)
    preferred_market     VARCHAR(100),         -- mercado mais apostado
    preferred_bet_type   VARCHAR(100),         -- tipo de aposta mais frequente
    live_bet_pct         NUMERIC(5,2),         -- percentual de apostas ao vivo (0-100)
    peak_hour            INTEGER,              -- hora do dia com mais apostas (0-23)
    updated_at           TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 5: Criar `sql/gold/005_create_crm_performance.sql`**

```sql
-- Tabela Gold: performance agregada por nível CRM
-- Consumida por: dashboard (visão por CRM), agente (perguntas por nível)
CREATE TABLE IF NOT EXISTS gold.crm_performance (
    crm_level                  VARCHAR(50) PRIMARY KEY,  -- nível CRM
    customer_count             INTEGER,                  -- clientes nesse nível
    total_bets                 INTEGER,                  -- total de apostas
    total_turnover             NUMERIC(12,2),            -- soma do valor apostado
    total_winnings             NUMERIC(12,2),            -- soma dos ganhos
    gross_revenue              NUMERIC(12,2),            -- receita bruta total
    avg_bets_per_customer      NUMERIC(10,2),            -- média de apostas por cliente
    avg_turnover_per_customer  NUMERIC(12,2),            -- média de turnover por cliente
    avg_gross_revenue_per_customer NUMERIC(12,2),        -- média de GR por cliente
    updated_at                 TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 6: Criar `sql/gold/006_create_season_summary.sql`**

```sql
-- Tabela Gold: resumo mensal da temporada
-- Granularidade: 1 linha por mês da temporada (Set/2018 a Ago/2019)
-- Consumida por: dashboard (evolução temporal), agente (visão geral da temporada)
CREATE TABLE IF NOT EXISTS gold.season_summary (
    month              DATE         PRIMARY KEY,  -- primeiro dia do mês
    total_customers    INTEGER,                   -- clientes únicos ativos no mês
    new_customers      INTEGER,                   -- clientes com primeira aposta no mês
    churned_customers  INTEGER,                   -- clientes sem aposta nos últimos 3 meses
    total_bets         INTEGER,                   -- total de apostas no mês
    total_turnover     NUMERIC(12,2),             -- soma do turnover no mês
    total_winnings     NUMERIC(12,2),             -- soma dos ganhos no mês
    gross_revenue      NUMERIC(12,2),             -- receita bruta do mês
    live_bet_pct       NUMERIC(5,2),              -- % de apostas ao vivo no mês
    updated_at         TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 7: Criar `sql/gold/007_create_cashout_analysis.sql`**

```sql
-- Tabela Gold: análise mensal de adoção e performance do cash out
-- Cash out foi funcionalidade nova introduzida na temporada
-- Consumida por: dashboard (análise de cash out), agente
CREATE TABLE IF NOT EXISTS gold.cashout_analysis (
    month                 DATE         PRIMARY KEY,  -- primeiro dia do mês
    total_attempts        INTEGER,                   -- total de tentativas
    successful_attempts   INTEGER,                   -- tentativas com sucesso
    failed_attempts       INTEGER,                   -- tentativas com falha
    success_rate          NUMERIC(5,2),              -- taxa de sucesso (%)
    total_cashout_amount  NUMERIC(12,2),             -- valor total sacado
    avg_cashout_amount    NUMERIC(12,2),             -- valor médio por tentativa
    updated_at            TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 8: Commit**

```bash
git add sql/gold/
git commit -m "feat: adicionar DDLs da camada Gold com tabelas analíticas"
```

---

## Task 8: Criar Docker Compose, Dockerfile e script de inicialização

**Files:**
- Create: `docker/init.sql`
- Create: `docker-compose.yml`
- Create: `Dockerfile`

- [ ] **Step 1: Criar `docker/init.sql`**

Este script consolida todos os DDLs e é executado pelo PostgreSQL na inicialização do container.

```sql
-- Script de inicialização do banco de dados
-- Executado automaticamente pelo PostgreSQL ao criar o container
-- Cria os 3 schemas e todas as tabelas da arquitetura medalhão

-- =========================================================
-- SCHEMA BRONZE — dados brutos dos CSVs
-- =========================================================
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.cashouts (
    cashout_attempt_bet_id          TEXT,
    cashout_attempt_bet_cashout_id  TEXT,
    cashout_attempt_bet_cashout_created TEXT,
    cashout_attempt_bet_cashout_status  TEXT,
    cashout_attempt_cashout_amount      TEXT,
    ingested_at                         TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.customer (
    customer_id              TEXT,
    customer_datecreation_id TEXT,
    customer_gender_name     TEXT,
    customer_birthday        TEXT,
    ingested_at              TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.customer_crm_level (
    customer_id    TEXT,
    date_yearmonth TEXT,
    crm_level      TEXT,
    ingested_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.events (
    event_id         TEXT,
    event_sport_name TEXT,
    event_class_name TEXT,
    event_type_name  TEXT,
    event_name       TEXT,
    event_start_time TEXT,
    event_end_time   TEXT,
    ingested_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.sportsbook (
    sportbetsettled_bet_id      TEXT,
    bettype_name                TEXT,
    market_template_name        TEXT,
    sportbetsettled_customer_id TEXT,
    sportbetsettled_settled     TEXT,
    sportbetsettled_placed      TEXT,
    channel_name                TEXT,
    sportbetsettled_event_id    TEXT,
    turnover                    TEXT,
    winnings                    TEXT,
    ingested_at                 TIMESTAMP DEFAULT NOW()
);

-- =========================================================
-- SCHEMA SILVER — dados limpos com regras de negócio
-- =========================================================
CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.customer (
    customer_id        INTEGER PRIMARY KEY,
    registration_date  DATE NOT NULL,
    gender             VARCHAR(20),
    birth_date         DATE,
    age                INTEGER,
    ingested_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.customer_crm_level (
    customer_id  INTEGER  NOT NULL,
    year_month   DATE     NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);

CREATE TABLE IF NOT EXISTS silver.events (
    event_id    INTEGER PRIMARY KEY,
    sport_name  VARCHAR(100),
    class_name  VARCHAR(100),
    type_name   VARCHAR(100),
    event_name  VARCHAR(255),
    start_time  TIMESTAMP,
    end_time    TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.sportsbook (
    bet_id         TEXT         PRIMARY KEY,
    bet_type       VARCHAR(100),
    market         VARCHAR(100),
    customer_id    INTEGER      NOT NULL,
    settled_at     TIMESTAMP,
    placed_at      TIMESTAMP    NOT NULL,
    channel        VARCHAR(50),
    event_id       INTEGER,
    turnover       NUMERIC(12,2) NOT NULL,
    winnings       NUMERIC(12,2) NOT NULL,
    gross_revenue  NUMERIC(12,2) NOT NULL,
    is_live        BOOLEAN       NOT NULL,
    ingested_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_customer ON silver.sportsbook (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_placed_at ON silver.sportsbook (placed_at);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_event ON silver.sportsbook (event_id);

CREATE TABLE IF NOT EXISTS silver.cashouts (
    bet_id          TEXT         NOT NULL,
    cashout_id      TEXT         PRIMARY KEY,
    created_at      TIMESTAMP    NOT NULL,
    status          VARCHAR(50)  NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_cashouts_bet ON silver.cashouts (bet_id);

-- =========================================================
-- SCHEMA GOLD — métricas e visões analíticas
-- =========================================================
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.customer_performance (
    customer_id          INTEGER PRIMARY KEY,
    gender               VARCHAR(20),
    age                  INTEGER,
    total_bets           INTEGER,
    total_turnover       NUMERIC(12,2),
    total_winnings       NUMERIC(12,2),
    gross_revenue        NUMERIC(12,2),
    live_bets            INTEGER,
    pre_event_bets       INTEGER,
    cashout_attempts     INTEGER,
    successful_cashouts  INTEGER,
    updated_at           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.customer_segments (
    customer_id     INTEGER PRIMARY KEY,
    segment         VARCHAR(20) NOT NULL,
    first_bet_date  DATE,
    last_bet_date   DATE,
    crm_level       VARCHAR(50),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.betting_preferences (
    customer_id          INTEGER PRIMARY KEY,
    preferred_channel    VARCHAR(50),
    preferred_market     VARCHAR(100),
    preferred_bet_type   VARCHAR(100),
    live_bet_pct         NUMERIC(5,2),
    peak_hour            INTEGER,
    updated_at           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.crm_performance (
    crm_level                      VARCHAR(50) PRIMARY KEY,
    customer_count                 INTEGER,
    total_bets                     INTEGER,
    total_turnover                 NUMERIC(12,2),
    total_winnings                 NUMERIC(12,2),
    gross_revenue                  NUMERIC(12,2),
    avg_bets_per_customer          NUMERIC(10,2),
    avg_turnover_per_customer      NUMERIC(12,2),
    avg_gross_revenue_per_customer NUMERIC(12,2),
    updated_at                     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.season_summary (
    month              DATE         PRIMARY KEY,
    total_customers    INTEGER,
    new_customers      INTEGER,
    churned_customers  INTEGER,
    total_bets         INTEGER,
    total_turnover     NUMERIC(12,2),
    total_winnings     NUMERIC(12,2),
    gross_revenue      NUMERIC(12,2),
    live_bet_pct       NUMERIC(5,2),
    updated_at         TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gold.cashout_analysis (
    month                 DATE         PRIMARY KEY,
    total_attempts        INTEGER,
    successful_attempts   INTEGER,
    failed_attempts       INTEGER,
    success_rate          NUMERIC(5,2),
    total_cashout_amount  NUMERIC(12,2),
    avg_cashout_amount    NUMERIC(12,2),
    updated_at            TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 2: Criar `Dockerfile`**

```dockerfile
# Imagem base Python 3.12 slim
FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar uv para gerenciamento de dependências
RUN pip install uv

# Copiar arquivos de configuração de dependências
COPY pyproject.toml .

# Instalar dependências do projeto via uv
RUN uv sync --no-dev

# Copiar o código-fonte
COPY src/ ./src/
COPY data/ ./data/

# Expor porta do Streamlit
EXPOSE 8501

# Comando padrão: iniciar o dashboard Streamlit
CMD ["uv", "run", "streamlit", "run", "src/dashboard/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

- [ ] **Step 3: Criar `docker-compose.yml`**

```yaml
# Serviços do projeto Sportsbook BI Analysis
# Uso: docker compose up -d
services:

  # Banco de dados PostgreSQL com arquitetura medalhão (bronze, silver, gold)
  postgres:
    image: postgres:16
    container_name: sportsbook_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      # Persistência dos dados entre reinicializações
      - postgres_data:/var/lib/postgresql/data
      # Script de inicialização: cria schemas e tabelas
      - ./docker/init.sql:/docker-entrypoint-initdb.d/init.sql
      # Dados raw disponíveis dentro do container para ingestão
      - ./data/raw:/data/raw
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

  # Aplicação: dashboard Streamlit + agente Agno
  app:
    build: .
    container_name: sportsbook_app
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      # Hot reload do código durante desenvolvimento
      - ./src:/app/src
      - ./data:/app/data
    ports:
      - "8501:8501"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

- [ ] **Step 4: Commit**

```bash
git add docker/ docker-compose.yml Dockerfile
git commit -m "feat: adicionar Docker Compose, Dockerfile e script de inicialização do banco"
```

---

## Task 9: Verificar ambiente Docker e criação dos schemas

- [ ] **Step 1: Copiar `.env.example` para `.env` e ajustar valores**

```bash
cp .env.example .env
```

Editar `.env`:
```
ANTHROPIC_API_KEY=<sua-chave>
POSTGRES_USER=sportsbook
POSTGRES_PASSWORD=sportsbook123
POSTGRES_DB=sportsbook_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://sportsbook:sportsbook123@localhost:5432/sportsbook_db
```

- [ ] **Step 2: Subir apenas o PostgreSQL para verificar**

```bash
docker compose up postgres -d
```

Saída esperada: container `sportsbook_postgres` rodando

- [ ] **Step 3: Verificar que os 3 schemas foram criados**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "\dn"
```

Saída esperada:
```
  List of schemas
  Name   |  Owner
---------+----------
 bronze  | sportsbook
 gold    | sportsbook
 public  | pg_database_owner
 silver  | sportsbook
```

- [ ] **Step 4: Verificar tabelas da camada Bronze**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "\dt bronze.*"
```

Saída esperada: 5 tabelas (cashouts, customer, customer_crm_level, events, sportsbook)

- [ ] **Step 5: Verificar tabelas da camada Silver**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "\dt silver.*"
```

Saída esperada: 5 tabelas (cashouts, customer, customer_crm_level, events, sportsbook)

- [ ] **Step 6: Verificar tabelas da camada Gold**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "\dt gold.*"
```

Saída esperada: 6 tabelas (cashout_analysis, betting_preferences, crm_performance, customer_performance, customer_segments, season_summary)

- [ ] **Step 7: Parar o container após verificação**

```bash
docker compose down
```

---

## Task 10: Criar CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Criar `CLAUDE.md`**

```markdown
# CLAUDE.md — Sportsbook BI Analysis

Leia este arquivo no início de toda sessão de desenvolvimento.
Ele é o contrato de trabalho do projeto.

## Visão Geral

Análise de dados da temporada de futebol romeno 2018/19 para o time de produto de Sportsbook.
O objetivo é avaliar a performance da temporada e preparar recomendações para a próxima.

**Repositório:** https://github.com/jurandircln/sportsbook-bi-analysis
**Temporada analisada:** Setembro 2018 – Agosto 2019

**Dados disponíveis (CSVs em `data/raw/`):**
- `Cashouts.csv` — tentativas de cash out
- `Customer.csv` — base de clientes
- `Customer_crm_level.csv` — níveis CRM mensais
- `Events.csv` — eventos esportivos
- `Sportsbook.csv` — atividade de apostas

## Regras de Código

- **Todos os comentários devem ser escritos em português**
- Nomes de arquivos: `snake_case`
- Funções e variáveis: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Classes: `PascalCase`
- Commits: Conventional Commits — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`

## Metodologia SDD — 3 Camadas de Contexto

O projeto segue Spec-Driven Development. Consulte as camadas antes de implementar:

| Camada | Localização | Pergunta respondida |
|---|---|---|
| Negócio | `docs/business-context/` | Por que estamos construindo isso? |
| Produto | `docs/product-context/` | O que estamos construindo? |
| Engenharia | `docs/technical-context/` | Como estamos construindo? |

## Arquitetura de Dados

Arquitetura **Medalhão** com 3 schemas no PostgreSQL:

| Camada | Schema | Propósito |
|---|---|---|
| Bronze | `bronze` | Dados brutos dos CSVs, tipos TEXT, sem transformação |
| Silver | `silver` | Dados tipados com regras de negócio aplicadas |
| Gold | `gold` | Métricas analíticas prontas para consumo |

**Regras críticas da camada Silver:**
- `gross_revenue = turnover - winnings`
- `is_live = placed_at >= event_start_time`
- CRM Level: forward-fill para meses sem registro
- Segmentos: novo / existente / saindo (ver ADR-002)

**Catálogo de dados:** `docs/technical-context/data-catalog/`

## Skills Disponíveis

| Skill | Quando invocar | Arquivo |
|---|---|---|
| `db-modeling` | Ao criar ou alterar qualquer tabela/schema | `.claude/skills/db-modeling.md` |
| `create-adr` | Ao tomar decisão técnica relevante com alternativas | `.claude/skills/create-adr.md` |
| `update-business-rules` | Ao alterar transformações da Silver | `.claude/skills/update-business-rules.md` |
| `update-data-catalog` | Ao adicionar/alterar tabelas, colunas ou métricas | `.claude/skills/update-data-catalog.md` |

## ADRs Ativos

| ADR | Título | Status |
|---|---|---|
| ADR-001 | Arquitetura Medalhão com PostgreSQL | Aceita |
| ADR-002 | Modelagem Inicial do Banco de Dados | Aceita |
| ADR-003 | Design do Agente Agno — Abordagem Híbrida | Aceita |
| ADR-004 | Stack e Ferramentas | Aceita |
| ADR-005 | Catálogo de Dados como Artefato de Governança | Aceita |

Localização: `docs/technical-context/adr/`

## Governança

### Quando criar um ADR
- Ao adotar nova tecnologia ou biblioteca
- Ao definir padrão arquitetural
- Ao rejeitar abordagem que parecia óbvia
- Ao fazer mudança que quebra padrão anterior
→ Invocar skill `create-adr`

### Quando atualizar o catálogo de dados
- Ao adicionar tabela, coluna ou schema novos
- Ao criar métricas derivadas na Gold
- Ao alterar tipos de dados
→ Invocar skill `update-data-catalog`

### Quando atualizar business-rules.md
- Ao alterar transformação da Silver
- Ao identificar nova regra de negócio
→ Invocar skill `update-business-rules`

## Stack

Ver detalhes em `docs/technical-context/stack.md`.

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12+ |
| Dependências | uv |
| Banco | PostgreSQL 16 |
| Infraestrutura | Docker + Docker Compose |
| Dashboard | Streamlit |
| Agente de BI | Agno (Python) |
| LLM | Claude via Anthropic API |

## Como Rodar o Projeto

```bash
# 1. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com sua ANTHROPIC_API_KEY

# 2. Subir todos os serviços
docker compose up -d

# 3. Verificar containers
docker compose ps

# 4. Acessar o dashboard
# http://localhost:8501

# 5. Conectar ao banco (desenvolvimento)
docker compose exec postgres psql -U sportsbook -d sportsbook_db
```

**Comandos úteis:**
```bash
docker compose logs -f          # ver logs em tempo real
docker compose down             # parar serviços
docker compose down -v          # parar e remover volumes (reset do banco)
uv sync                         # instalar/atualizar dependências Python
uv run pytest                   # executar testes
```
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: criar CLAUDE.md com guia completo do projeto"
```

---

## Task 11: Criar documentação SDD — Contexto de Negócio

**Files:**
- Create: `docs/business-context/vision.md`
- Create: `docs/business-context/personas.md`
- Create: `docs/business-context/journeys.md`
- Create: `docs/business-context/competitive.md`
- Create: `docs/business-context/kpis.md`

- [ ] **Step 1: Criar `docs/business-context/vision.md`**

```markdown
# Visão Estratégica

## O Produto

Plataforma de Sportsbook (apostas esportivas) que permite aos clientes apostar em
eventos esportivos em tempo real (Live) e antes dos eventos (Pre-event), com opção
de Cash Out para encerramento antecipado de apostas.

## Problema Central

O time de produto precisa avaliar a performance da temporada de futebol romeno 2018/19
para entender o comportamento da base de clientes, identificar oportunidades de crescimento
e preparar estratégias para a próxima temporada.

## Diferencial

Combinação de apostas ao vivo com funcionalidade de Cash Out (novidade desta temporada),
oferecendo maior controle ao apostador.

## Horizonte Atual

Avaliar a temporada 2018/19, identificar padrões de comportamento por segmento de cliente
e CRM level, e transformar esses dados em recomendações acionáveis para a temporada seguinte.

## Contexto da Análise

- **Temporada:** Futebol Romeno 2018/19
- **Período:** Setembro 2018 – Agosto 2019 (12 meses)
- **Novidade da temporada:** Cash Out (funcionalidade recém-lançada)
- **Dados disponíveis:** Apostas, Clientes, Níveis CRM, Eventos, Cash Outs
```

- [ ] **Step 2: Criar `docs/business-context/personas.md`**

```markdown
# Personas

## Persona: Analista de Produto (Audiência Principal)

**Perfil:** Analista ou gerente de produto do time de Sportsbook, nível técnico médio,
familiarizado com métricas de apostas e comportamento de usuário.

**Objetivo principal:** Entender a performance da temporada e identificar oportunidades
para a próxima temporada com base em dados.

**Dores:** Dados fragmentados em múltiplas fontes, demora para consolidar métricas,
dificuldade de comparar segmentos de clientes rapidamente.

**Definição de sucesso:** Conseguir responder perguntas de negócio sobre a temporada
em minutos, com dados confiáveis e visualizações claras.

---

## Persona: Cliente Apostador

**Perfil:** Usuário final da plataforma, diversas faixas etárias e gêneros,
acessa via dispositivo móvel (Android/iOS) ou web.

**Objetivo principal:** Apostar em eventos de futebol e maximizar seus ganhos.

**Dores:** Incerteza sobre apostas em andamento, desejo de encerrar apostas antecipadamente.

**Definição de sucesso:** Realizar apostas com facilidade e usar o Cash Out quando necessário.
```

- [ ] **Step 3: Criar `docs/business-context/journeys.md`**

```markdown
# Jornadas do Usuário

## Jornada: Análise da Temporada — Analista de Produto

**Objetivo:** Obter visão completa da performance da temporada para apresentação ao time.

**Etapas:**
1. Analista acessa o dashboard → visualiza KPIs consolidados da temporada
2. Analista filtra por período ou CRM level → métricas atualizam dinamicamente
3. Analista identifica segmento de interesse → drill-down em clientes novos/existentes/saindo
4. Analista quer resposta específica → usa o chat do agente de BI
5. Analista exporta insights → prepara apresentação para o time de produto

**Resultado esperado:** Conjunto de insights acionáveis sobre a temporada.

**Pontos de fricção conhecidos:** Volume de dados grande, necessidade de cruzar múltiplas
dimensões simultaneamente.

---

## Jornada: Aposta ao Vivo — Cliente Apostador

**Objetivo:** Realizar aposta em evento em andamento e gerenciar posição via Cash Out.

**Etapas:**
1. Cliente acessa a plataforma durante o evento
2. Seleciona evento → visualiza odds em tempo real
3. Realiza aposta ao vivo
4. Acompanha o evento → decide usar Cash Out se necessário
5. Cash Out executado → valor creditado na conta

**Resultado esperado:** Aposta liquidada com controle do risco.

**Pontos de fricção conhecidos:** Taxa de sucesso do Cash Out é nova e pode gerar
expectativas não atendidas em caso de falha.
```

- [ ] **Step 4: Criar `docs/business-context/competitive.md`**

```markdown
# Panorama Competitivo

Contexto simplificado para a análise interna da temporada.

## Mercado de Apostas Esportivas Online

| Concorrente | Pontos Fortes | Nossa Diferenciação |
|---|---|---|
| Bet365 | Variedade de mercados, odds competitivas | Foco no mercado local romeno |
| Unibet | UX, mercado europeu consolidado | Cash Out como diferencial tático |
| Betano | Forte no mercado romeno | Análise aprofundada de CRM levels |

## Observação

O diferencial desta análise não é produto vs. concorrente, mas sim a capacidade de
entender a base de clientes em profundidade via CRM levels e segmentação comportamental.
```

- [ ] **Step 5: Criar `docs/business-context/kpis.md`**

```markdown
# KPIs e Métricas de Sucesso

## Métricas Principais

| Métrica | Definição | Fórmula |
|---|---|---|
| Gross Revenue (GR) | Receita bruta da operação | `Turnover - Winnings` |
| Turnover | Volume total apostado | Soma dos valores apostados |
| Winnings | Total pago aos clientes | Soma dos ganhos dos clientes |
| Margem | Percentual retido pela casa | `Gross Revenue / Turnover * 100` |

## Métricas de Base de Clientes

| Métrica | Definição |
|---|---|
| Clientes Novos | Primeira aposta realizada durante a temporada |
| Clientes Existentes | Apostas antes E durante a temporada |
| Clientes Saindo | Apostas antes da temporada, inativos nos últimos 3 meses |
| Clientes Ativos | Pelo menos 1 aposta no mês analisado |

## Métricas de Preferência

| Métrica | Definição |
|---|---|
| Live Bet % | Percentual de apostas feitas após início do evento |
| Canal Preferido | Dispositivo mais usado por cliente (Android, iOS, Web) |
| Mercado Preferido | Tipo de aposta mais frequente por cliente |
| Horário de Pico | Hora do dia com maior volume de apostas |

## Métricas de Cash Out

| Métrica | Definição |
|---|---|
| Taxa de Adoção | % de apostadores que usaram Cash Out |
| Taxa de Sucesso | Cash outs bem-sucedidos / total de tentativas |
| Valor Médio | Média do valor por tentativa de Cash Out |

## Metas da Análise

O objetivo desta análise não é atingir metas futuras, mas compreender a performance
passada da temporada 2018/19 e gerar recomendações para a próxima temporada.
```

- [ ] **Step 6: Commit**

```bash
git add docs/business-context/
git commit -m "docs: criar contexto de negócio SDD (visão, personas, jornadas, KPIs)"
```

---

## Task 12: Criar documentação SDD — Contexto de Produto e Engenharia

**Files:**
- Create: `docs/product-context/business-rules.md`
- Create: `docs/product-context/glossary.md`
- Create: `docs/technical-context/stack.md`
- Create: `docs/technical-context/codebase-guide.md`
- Create: `.cursor/rules/global.mdc`

- [ ] **Step 1: Criar `docs/product-context/business-rules.md`**

```markdown
# Regras de Negócio

Regras aplicadas na camada Silver da arquitetura medalhão.
**Qualquer alteração aqui deve ser acompanhada de atualização no código de transformação.**

## RN-001: Cálculo de Gross Revenue

**Descrição:** Receita bruta é calculada como a diferença entre o valor apostado e os ganhos do cliente.
**Fórmula:** `gross_revenue = turnover - winnings`
**Aplica-se a:** `silver.sportsbook`, `gold.customer_performance`, `gold.crm_performance`, `gold.season_summary`
**Exceções:** Nenhuma.

## RN-002: Classificação Live vs. Pre-event

**Descrição:** Uma aposta é considerada "ao vivo" quando foi feita após o início do evento.
**Fórmula:** `is_live = (placed_at >= event_start_time)`
**Aplica-se a:** `silver.sportsbook`
**Exceções:** Se `event_start_time` for nulo, a aposta é classificada como Pre-event.

## RN-003: Forward-fill do CRM Level

**Descrição:** O CRM Level de um cliente em um mês sem registro é o nível mais recentemente atribuído.
**Exemplo:** Cliente Bronze em Out/18 e Silver em Jan/19 → nível de Nov/18 e Dez/18 é Bronze.
**Aplica-se a:** `silver.customer_crm_level`
**Exceções:** Para meses anteriores ao primeiro registro do cliente, CRM Level é NULL.

## RN-004: Segmentação de Clientes

**Descrição:** Classifica cada cliente em relação à temporada (Set/2018–Ago/2019).
- **novo**: primeira aposta ocorreu dentro da temporada
- **existente**: apostas antes E durante a temporada
- **saindo**: tinha apostas antes da temporada, mas ficou inativo nos últimos 3 meses dela

**Aplica-se a:** `gold.customer_segments`
**Exceções:** Clientes sem nenhuma aposta na temporada não aparecem na Gold.

## RN-005: Período da Temporada

**Descrição:** A temporada de futebol romeno 2018/19 abrange de Setembro/2018 a Agosto/2019.
**Aplica-se a:** Todos os filtros temporais da análise.
**Exceções:** Dados históricos anteriores à temporada são usados para classificação de
segmento (existente vs. novo), mas não entram nas métricas de performance da temporada.
```

- [ ] **Step 2: Criar `docs/product-context/glossary.md`**

```markdown
# Glossário

Termos técnicos e de negócio utilizados no projeto.

| Termo | Definição |
|---|---|
| Turnover | Valor total apostado pelo cliente. Equivale a receita bruta antes de descontar ganhos. |
| Winnings | Valor pago ao cliente quando ele ganha uma aposta. |
| Gross Revenue (GR) | Receita líquida da operação: Turnover - Winnings. Métrica principal de performance. |
| Cash Out | Funcionalidade que permite ao cliente encerrar uma aposta antes do resultado, recebendo um valor parcial. Novidade na temporada 2018/19. |
| Live Betting | Aposta realizada após o início do evento. Identificada por: placed_at >= event_start_time. |
| Pre-event Betting | Aposta realizada antes do início do evento. |
| CRM Level | Nível de relacionamento do cliente (ex: Bronze, Silver, Gold). Atribuído mensalmente. |
| Forward-fill | Técnica de preenchimento de dados onde valores ausentes recebem o último valor conhecido. Usado nos CRM Levels. |
| Segmento | Classificação do cliente em relação à temporada: novo, existente ou saindo. |
| Temporada 2018/19 | Período de análise: Setembro 2018 a Agosto 2019 (12 meses). |
| Bronze (camada) | Primeira camada do medalhão: dados brutos dos CSVs. |
| Silver (camada) | Segunda camada: dados tipados com regras de negócio. |
| Gold (camada) | Terceira camada: métricas analíticas para consumo. |
```

- [ ] **Step 3: Criar `docs/technical-context/stack.md`**

```markdown
# Stack e Convenções

## Stack

| Camada | Tecnologia | Versão | Observação |
|---|---|---|---|
| Linguagem | Python | 3.12+ | — |
| Dependências | uv | latest | Substitui pip/poetry |
| Banco de dados | PostgreSQL | 16 | Schemas: bronze, silver, gold |
| Infraestrutura | Docker + Compose | latest | Portabilidade total |
| Dashboard | Streamlit | >=1.32 | Interface analítica |
| Agente de IA | Agno | >=1.4 | Framework de agentes Python |
| LLM | Claude (Anthropic) | API | Via ANTHROPIC_API_KEY |
| Visualizações | Plotly | >=5.20 | Gráficos interativos no Streamlit |
| ORM/DB | SQLAlchemy | >=2.0 | Conexão Python-PostgreSQL |
| Driver DB | psycopg2-binary | >=2.9 | Adaptador PostgreSQL para Python |

## Convenções de Código

### Nomenclatura
- Arquivos Python: `snake_case.py`
- Funções e variáveis: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Arquivos SQL: `NNN_descricao.sql` (numerados para ordenação)
- Tabelas e colunas SQL: `snake_case`

### Comentários
**Todos os comentários devem ser escritos em português.**

### Branches
- `main` — código estável
- `feature/*` — novas funcionalidades
- `fix/*` — correções
- `docs/*` — documentação

### Commits
Seguir Conventional Commits:
- `feat:` — nova funcionalidade
- `fix:` — correção de bug
- `docs:` — documentação
- `chore:` — tarefas de manutenção
- `refactor:` — refatoração sem mudança de comportamento

## Variáveis de Ambiente

Ver `.env.example` para lista completa.
Nunca commitar o arquivo `.env`.
```

- [ ] **Step 4: Criar `docs/technical-context/codebase-guide.md`**

```markdown
# Guia do Codebase

## Estrutura de Diretórios

```
src/
├── ingestion/        ← scripts de carga Bronze: lê CSVs e insere em bronze.*
├── transformation/   ← transformações Silver e Gold: aplica regras de negócio
├── agent/            ← agente Agno com tools SQL e integração Claude
└── dashboard/        ← aplicação Streamlit com abas de análise e chat

sql/
├── bronze/           ← DDLs das tabelas bronze.* (referência de schema)
├── silver/           ← DDLs das tabelas silver.*
└── gold/             ← DDLs das tabelas gold.*

docker/
└── init.sql          ← script executado na inicialização do PostgreSQL
```

## Padrão Arquitetural

O projeto segue separação por responsabilidade de dados:

1. **Ingestion** lê os CSVs de `data/raw/` e insere na Bronze sem transformação.
   Cada arquivo CSV tem um script de ingestão correspondente.

2. **Transformation** lê da Bronze, aplica regras de negócio e escreve na Silver.
   Em seguida, agrega da Silver para a Gold. Cada camada tem módulo separado.

3. **Agent** expõe tools SQL que consultam a Gold. Integra com Claude via Agno.
   O system prompt inclui schema da Gold e regras de negócio do catálogo.

4. **Dashboard** consome a Gold diretamente via SQLAlchemy para visualizações,
   e chama o agente para respostas conversacionais.

## Fluxo de Dados

```
data/raw/*.csv
    ↓ (ingestion/)
bronze.* (dados brutos)
    ↓ (transformation/silver/)
silver.* (dados limpos + regras de negócio)
    ↓ (transformation/gold/)
gold.* (métricas analíticas)
    ↓               ↓
dashboard/        agent/
(Streamlit)    (Agno + Claude)
```

## Conexão com o Banco

Usar `DATABASE_URL` do `.env` via SQLAlchemy:

```python
# Exemplo de conexão (será implementado em src/ingestion/)
from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))
```
```

- [ ] **Step 5: Criar `.cursor/rules/global.mdc`**

```markdown
# Regras Globais do Projeto

Você está no projeto **Sportsbook BI Analysis**.

## Antes de qualquer implementação

1. Leia o `CLAUDE.md` na raiz do repositório
2. Consulte a camada de contexto relevante em `docs/`
3. Verifique se existe skill aplicável em `.claude/skills/`

## Regras de código

- Todos os comentários em **português**
- snake_case para arquivos, funções e variáveis
- PascalCase para classes
- UPPER_SNAKE_CASE para constantes

## Arquitetura

- Dados fluem: Bronze → Silver → Gold
- Nunca leia da Bronze no dashboard — use sempre a Gold
- Regras de negócio vivem na Silver, não na aplicação
- Toda decisão técnica relevante → criar ADR (skill: `create-adr`)
- Toda mudança de schema → atualizar catálogo (skill: `update-data-catalog`)
```

- [ ] **Step 6: Commit**

```bash
git add docs/product-context/ docs/technical-context/stack.md docs/technical-context/codebase-guide.md .cursor/
git commit -m "docs: criar contexto de produto, stack, codebase guide e regras do Cursor"
```

---

## Task 13: Criar skills do projeto

**Files:**
- Create: `.claude/skills/db-modeling.md`
- Create: `.claude/skills/create-adr.md`
- Create: `.claude/skills/update-business-rules.md`
- Create: `.claude/skills/update-data-catalog.md`

- [ ] **Step 1: Criar `.claude/skills/db-modeling.md`**

```markdown
# Skill: db-modeling

Use esta skill ao criar ou evoluir qualquer tabela, schema ou índice no banco de dados.

## Checklist obrigatório

- [ ] Consultar o ADR-002 (`docs/technical-context/adr/ADR-002-database-modeling.md`)
      para garantir aderência às decisões de modelagem já tomadas
- [ ] Verificar se a tabela já existe no catálogo de dados
      (`docs/technical-context/data-catalog/`)
- [ ] Definir a camada correta (Bronze, Silver ou Gold) e o propósito da tabela
- [ ] Usar TEXT para todas as colunas de tabelas Bronze
- [ ] Usar tipos precisos nas tabelas Silver:
      - IDs: INTEGER
      - Datas sem hora: DATE
      - Timestamps: TIMESTAMP
      - Valores monetários: NUMERIC(12,2)
      - Flags: BOOLEAN
      - Textos curtos: VARCHAR(N)
- [ ] Incluir coluna `ingested_at TIMESTAMP DEFAULT NOW()` em Bronze e Silver
- [ ] Incluir coluna `updated_at TIMESTAMP DEFAULT NOW()` em Gold
- [ ] Adicionar índices nas colunas usadas em JOINs e filtros frequentes
- [ ] Criar o DDL correspondente em `sql/<camada>/NNN_descricao.sql`
- [ ] Atualizar `docker/init.sql` com o novo DDL
- [ ] Atualizar o catálogo de dados (invocar skill `update-data-catalog`)
- [ ] Se a decisão for nova ou divergir do padrão, criar ADR (invocar skill `create-adr`)

## Padrão de nomenclatura SQL

- Schemas: `bronze`, `silver`, `gold`
- Tabelas: `snake_case` (ex: `customer_crm_level`)
- Colunas: `snake_case` (ex: `gross_revenue`)
- Índices: `idx_<schema>_<tabela>_<coluna>` (ex: `idx_silver_sportsbook_customer`)
- PKs: declaradas inline na coluna quando simples, ou como constraint quando composta

## Template de DDL Bronze

```sql
-- Tabela Bronze: <descrição>
-- Fonte: <arquivo CSV de origem>
CREATE TABLE IF NOT EXISTS bronze.<nome> (
    <coluna_id>  TEXT,
    <coluna_2>   TEXT,
    ...
    ingested_at  TIMESTAMP DEFAULT NOW()
);
```

## Template de DDL Silver

```sql
-- Tabela Silver: <descrição>
-- Regras de negócio aplicadas: <listar regras>
-- Fonte: bronze.<tabela_origem>
CREATE TABLE IF NOT EXISTS silver.<nome> (
    <id>         INTEGER PRIMARY KEY,
    <coluna_2>   <TIPO> NOT NULL,
    ...
    ingested_at  TIMESTAMP DEFAULT NOW()
);
```

## Template de DDL Gold

```sql
-- Tabela Gold: <descrição>
-- Consumida por: <dashboard / agente / ambos>
CREATE TABLE IF NOT EXISTS gold.<nome> (
    <id>         <TIPO> PRIMARY KEY,
    <metrica_1>  NUMERIC(12,2),
    ...
    updated_at   TIMESTAMP DEFAULT NOW()
);
```
```

- [ ] **Step 2: Criar `.claude/skills/create-adr.md`**

```markdown
# Skill: create-adr

Use esta skill ao tomar qualquer decisão técnica relevante que tenha alternativas consideradas.

## Quando criar um ADR

- Ao adotar nova tecnologia, biblioteca ou framework
- Ao definir padrão arquitetural
- Ao rejeitar abordagem que parecia óbvia
- Ao fazer mudança que quebra padrão anterior
- Ao definir convenção que afeta todo o projeto

## Checklist

- [ ] Verificar a numeração do próximo ADR em `docs/technical-context/adr/`
      (listar arquivos e usar próximo número disponível)
- [ ] Identificar o contexto: qual problema motivou a decisão?
- [ ] Descrever as alternativas consideradas (pelo menos 2)
- [ ] Documentar a decisão tomada e o motivo
- [ ] Listar as consequências (benefícios e trade-offs aceitos)
- [ ] Criar o arquivo `ADR-NNN-titulo-curto.md` em `docs/technical-context/adr/`
- [ ] Atualizar a tabela de ADRs no `CLAUDE.md`
- [ ] Se um ADR anterior for substituído, marcar como `Status: Substituída por ADR-NNN`

## Template

```markdown
# ADR-NNN: [Título curto e descritivo]

**Data:** YYYY-MM-DD
**Status:** [Proposta | Aceita | Substituída por ADR-XXX]

## Contexto

[Descreva o problema. O que estava acontecendo? Quais eram as restrições?]

## Decisão

[O que foi decidido, de forma direta.]

## Consequências

[O que muda? Quais benefícios? Quais trade-offs foram aceitos?]
```

## Exemplo de uso

Situação: você vai usar uma biblioteca nova para parsing de CSV.

1. Verificar: próximo ADR é ADR-006
2. Contexto: pandas era lento para os volumes testados
3. Decisão: adotar polars para leitura de CSV na ingestão
4. Consequências: parse 10x mais rápido, nova dependência, curva de aprendizado
5. Criar `ADR-006-adocao-polars-para-ingestao.md`
6. Atualizar CLAUDE.md
```

- [ ] **Step 3: Criar `.claude/skills/update-business-rules.md`**

```markdown
# Skill: update-business-rules

Use esta skill ao alterar qualquer transformação da camada Silver ou ao identificar
nova regra de negócio nos dados.

## Princípio

As regras de negócio vivem na Silver. Mudá-las sem documentar gera inconsistências
entre o que o código faz e o que a equipe acredita que ele faz.

## Checklist

- [ ] Identificar qual regra está sendo criada ou alterada
- [ ] Verificar se a regra já existe em `docs/product-context/business-rules.md`
- [ ] Atualizar ou criar a regra no documento, com:
      - ID da regra (RN-NNN)
      - Descrição clara
      - Fórmula ou lógica (quando aplicável)
      - Tabelas afetadas
      - Exceções conhecidas
- [ ] Atualizar o código de transformação correspondente em `src/transformation/`
- [ ] Verificar se o catálogo de dados precisa ser atualizado (coluna computada nova?)
      → Se sim, invocar skill `update-data-catalog`
- [ ] Se a mudança for significativa, criar ADR → invocar skill `create-adr`
- [ ] Commitar `business-rules.md` junto com o código de transformação na mesma PR/commit

## Regras já documentadas (referência rápida)

| ID | Regra | Fórmula |
|---|---|---|
| RN-001 | Gross Revenue | `turnover - winnings` |
| RN-002 | Live vs. Pre-event | `placed_at >= event_start_time` |
| RN-003 | CRM Level forward-fill | Último nível registrado |
| RN-004 | Segmentação de clientes | novo / existente / saindo |
| RN-005 | Período da temporada | Set/2018 – Ago/2019 |
```

- [ ] **Step 4: Criar `.claude/skills/update-data-catalog.md`**

```markdown
# Skill: update-data-catalog

Use esta skill ao adicionar ou alterar tabelas, colunas ou métricas derivadas
em qualquer camada da arquitetura medalhão.

## Princípio

O catálogo de dados é a fonte de verdade sobre o que cada campo significa.
Sem ele, pessoas diferentes interpretam os mesmos dados de formas diferentes.

## Checklist

- [ ] Identificar qual tabela/coluna/métrica foi adicionada ou alterada
- [ ] Localizar o arquivo correto em `docs/technical-context/data-catalog/<camada>/`
- [ ] Atualizar ou criar o arquivo com:
      - Nome e propósito da tabela
      - Lista de colunas com: nome, tipo, descrição, valores possíveis (quando relevante)
      - Regras de negócio aplicadas (referenciar RN-NNN de business-rules.md)
      - Fonte de origem (para Silver/Gold: qual tabela upstream alimenta)
      - Exemplo de valores quando útil para clareza
- [ ] Verificar se `docs/technical-context/data-catalog/overview.md` precisa de atualização
- [ ] Commitar o catálogo junto com o DDL ou código na mesma PR/commit

## Estrutura dos arquivos do catálogo

```markdown
# Catálogo: <schema>.<tabela>

**Descrição:** [o que esta tabela representa]
**Camada:** [Bronze | Silver | Gold]
**Fonte:** [origem dos dados]
**Atualização:** [quando é populada/atualizada]

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| nome_coluna | TIPO | descrição | — |

## Regras de Negócio Aplicadas

- [RN-NNN]: [descrição resumida]

## Notas

[Observações importantes, armadilhas conhecidas, exemplos]
```

## Localização no repositório

```
docs/technical-context/data-catalog/
├── overview.md           ← visão geral do catálogo
├── bronze/
│   ├── cashouts.md
│   ├── customer.md
│   ├── customer_crm_level.md
│   ├── events.md
│   └── sportsbook.md
├── silver/
│   └── README.md         ← será populado no Plano 2
└── gold/
    └── README.md         ← será populado no Plano 2
```
```

- [ ] **Step 5: Commit**

```bash
git add .claude/
git commit -m "docs: criar skills de db-modeling, create-adr, update-business-rules e update-data-catalog"
```

---

## Task 14: Criar ADRs restantes (001, 003, 004, 005)

**Files:**
- Create: `docs/technical-context/adr/ADR-001-medallion-architecture.md`
- Create: `docs/technical-context/adr/ADR-003-agno-agent-design.md`
- Create: `docs/technical-context/adr/ADR-004-stack-and-tooling.md`
- Create: `docs/technical-context/adr/ADR-005-data-catalog.md`

- [ ] **Step 1: Criar `docs/technical-context/adr/ADR-001-medallion-architecture.md`**

```markdown
# ADR-001: Arquitetura Medalhão com PostgreSQL

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

O projeto analisa dados de 5 CSVs com estruturas heterogêneas. Precisávamos de uma
arquitetura de dados que separasse claramente a ingestão bruta das transformações de
negócio, garantindo rastreabilidade e escalabilidade para análises futuras.

## Decisão

Adotar a Arquitetura Medalhão com 3 camadas (Bronze, Silver, Gold) implementadas como
schemas separados no PostgreSQL: `bronze`, `silver`, `gold`.

## Consequências

Separação clara de responsabilidades: Bronze preserva dados originais (nenhuma perda
por transformação incorreta), Silver centraliza regras de negócio (único ponto de verdade),
Gold é otimizada para leitura analítica (dashboard e agente consomem apenas Gold).
A estrutura por schemas no PostgreSQL mantém tudo em um único banco, simplificando
a infraestrutura Docker sem perder a separação lógica das camadas.
```

- [ ] **Step 2: Criar `docs/technical-context/adr/ADR-003-agno-agent-design.md`**

```markdown
# ADR-003: Design do Agente Agno — Abordagem Híbrida

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

O dashboard Streamlit precisa de uma aba conversacional onde o time de produto possa
fazer perguntas de negócio em linguagem natural. Avaliamos três abordagens: Text-to-SQL
puro (flexível mas instável), views pré-computadas (estável mas rígido) e abordagem
híbrida (SQL tools pré-definidas + ad-hoc com guardrails).

## Decisão

Adotar abordagem híbrida com o framework Agno:

1. **Tools pré-definidas**: cada bloco temático do brief vira uma tool Agno com SQL
   parametrizável — `get_customer_performance`, `get_customer_segments`,
   `get_betting_preferences`, `get_crm_performance`, `get_season_summary`,
   `get_cashout_analysis`.

2. **Modo ad-hoc**: para perguntas fora do escopo das tools, o agente gera SQL com
   o schema da Gold e as regras de negócio no system prompt como guardrail.

3. **LLM**: Claude (Anthropic) via API, com `ANTHROPIC_API_KEY` em `.env`.

4. **System prompt**: inclui schema completo das tabelas Gold, definições do catálogo
   de dados e regras de negócio críticas (Gross Revenue, CRM forward-fill, segmentos).

## Consequências

As perguntas mapeadas têm resposta precisa e consistente via tools. Perguntas ad-hoc
têm margem de erro maior, mas o schema estruturado no system prompt reduz alucinações.
Aceita-se a dependência do framework Agno e da API Anthropic como componentes críticos.
```

- [ ] **Step 3: Criar `docs/technical-context/adr/ADR-004-stack-and-tooling.md`**

```markdown
# ADR-004: Stack e Ferramentas

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

Precisávamos definir a stack completa do projeto garantindo: reprodutibilidade
do ambiente, velocidade de desenvolvimento, suporte a análise de dados e
integração com IA generativa.

## Decisão

- **Python 3.12** com **uv** para gerenciamento de dependências (mais rápido que pip/poetry)
- **PostgreSQL 16** como banco de dados (suporte completo a schemas, NUMERIC, índices)
- **Docker + Docker Compose** para portabilidade — qualquer dev sobe o ambiente com `docker compose up`
- **Streamlit** para o dashboard analítico (Python nativo, sem frontend separado)
- **Agno** como framework de agentes (Python nativo, suporte a tools e múltiplos LLMs)
- **Claude (Anthropic)** como LLM do agente (qualidade de raciocínio e SQL generation)
- **Plotly** para gráficos interativos dentro do Streamlit
- **SQLAlchemy 2.0** para conexão Python-PostgreSQL

## Consequências

Stack 100% Python reduz a curva de aprendizado. Docker garante que novos devs não
precisem configurar banco localmente. uv é significativamente mais rápido que pip
para instalar dependências. Aceita-se dependência de serviço externo (API Anthropic)
para funcionar o agente — sem a chave, o dashboard funciona mas o chat não.
```

- [ ] **Step 4: Criar `docs/technical-context/adr/ADR-005-data-catalog.md`**

```markdown
# ADR-005: Catálogo de Dados como Artefato de Governança Obrigatório

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

Em projetos de dados com múltiplas fontes e transformações, é comum que pessoas
diferentes interpretem os mesmos campos de formas distintas. Exemplo: "Gross Revenue"
poderia ser interpretado como `turnover`, `winnings` ou `turnover - winnings`.
Sem uma fonte de verdade documentada, o sistema de BI perde confiabilidade.

## Decisão

O catálogo de dados é um artefato de governança obrigatório, versionado junto com
o código no repositório. Localizado em `docs/technical-context/data-catalog/`,
organizado por camada medalhão.

**Protocolo:** Qualquer alteração de schema ou nova métrica derivada exige atualização
do catálogo na mesma PR/commit. A skill `update-data-catalog` deve ser invocada
sempre que houver mudança estrutural nos dados.

O catálogo documenta por tabela: descrição, colunas com tipos e definições,
regras de negócio aplicadas, fonte de origem e exemplos quando relevante.

## Consequências

Governança explícita garante que o agente de BI, o dashboard e os desenvolvedores
trabalhem com a mesma definição de cada campo. O custo é a disciplina de manter
o catálogo atualizado a cada mudança — minimizado pela skill `update-data-catalog`.
```

- [ ] **Step 5: Commit**

```bash
git add docs/technical-context/adr/
git commit -m "docs: criar ADRs 001, 003, 004 e 005 — decisões arquiteturais do projeto"
```

---

## Task 15: Criar catálogo de dados — camada Bronze

**Files:**
- Create: `docs/technical-context/data-catalog/overview.md`
- Create: `docs/technical-context/data-catalog/bronze/cashouts.md`
- Create: `docs/technical-context/data-catalog/bronze/customer.md`
- Create: `docs/technical-context/data-catalog/bronze/customer_crm_level.md`
- Create: `docs/technical-context/data-catalog/bronze/events.md`
- Create: `docs/technical-context/data-catalog/bronze/sportsbook.md`
- Create: `docs/technical-context/data-catalog/silver/README.md`
- Create: `docs/technical-context/data-catalog/gold/README.md`

- [ ] **Step 1: Criar `docs/technical-context/data-catalog/overview.md`**

```markdown
# Catálogo de Dados — Visão Geral

O catálogo de dados é a fonte de verdade sobre o significado de cada campo,
tabela e métrica do projeto. Ele previne que pessoas diferentes interpretem
os mesmos dados de formas distintas.

## Como usar

Antes de implementar qualquer análise, query ou feature do agente, consulte
o catálogo para entender o que cada campo representa e quais regras foram aplicadas.

## Organização

O catálogo segue a mesma estrutura da arquitetura medalhão:

| Camada | Localização | Conteúdo |
|---|---|---|
| Bronze | `bronze/` | Dados brutos dos CSVs, tipos TEXT |
| Silver | `silver/` | Dados transformados com regras de negócio |
| Gold | `gold/` | Métricas analíticas para consumo |

## Protocolo de Atualização

Qualquer alteração de schema ou nova métrica → invocar skill `update-data-catalog`.
O catálogo é commitado junto com o DDL ou código na mesma PR/commit.

## Fontes de Dados

Todos os dados são da temporada de futebol romeno 2018/19 (Set/2018 – Ago/2019).

| Arquivo CSV | Tabela Bronze | Descrição |
|---|---|---|
| Cashouts.csv | bronze.cashouts | Tentativas de cash out |
| Customer.csv | bronze.customer | Base de clientes |
| Customer_crm_level.csv | bronze.customer_crm_level | Níveis CRM mensais |
| Events.csv | bronze.events | Eventos esportivos |
| Sportsbook.csv | bronze.sportsbook | Atividade de apostas |
```

- [ ] **Step 2: Criar `docs/technical-context/data-catalog/bronze/cashouts.md`**

```markdown
# Catálogo: bronze.cashouts

**Descrição:** Tentativas de uso da funcionalidade Cash Out por clientes apostadores.
Cash Out é uma novidade desta temporada (2018/19) — permite encerrar a aposta antes
do resultado e receber um valor parcial.
**Camada:** Bronze
**Fonte:** Cashouts.csv
**Atualização:** Ingestão única dos dados históricos da temporada

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| cashout_attempt_bet_id | TEXT | ID da aposta relacionada à tentativa | — |
| cashout_attempt_bet_cashout_id | TEXT | ID único da tentativa de cash out | — |
| cashout_attempt_bet_cashout_created | TEXT | Timestamp da tentativa (raw do CSV) | — |
| cashout_attempt_bet_cashout_status | TEXT | Resultado da tentativa | Verificar valores únicos após ingestão |
| cashout_attempt_cashout_amount | TEXT | Valor do cash out solicitado (raw) | Numérico como texto |
| ingested_at | TIMESTAMP | Momento da ingestão no banco | — |

## Notas

- Todos os campos são TEXT na Bronze. Tipos corretos são aplicados na Silver.
- Uma aposta pode ter múltiplas tentativas de cash out.
- O status deve ser analisado após ingestão para identificar os valores possíveis.
```

- [ ] **Step 3: Criar `docs/technical-context/data-catalog/bronze/customer.md`**

```markdown
# Catálogo: bronze.customer

**Descrição:** Base de clientes da plataforma de Sportsbook.
**Camada:** Bronze
**Fonte:** Customer.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| customer_id | TEXT | ID único do cliente | Numérico como texto |
| customer_datecreation_id | TEXT | Data de cadastro do cliente na plataforma (raw) | — |
| customer_gender_name | TEXT | Gênero do cliente | Verificar após ingestão |
| customer_birthday | TEXT | Data de nascimento (raw) | — |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Notas

- `customer_id` é numérico mas armazenado como TEXT na Bronze.
- Data de nascimento pode conter valores nulos ou inconsistentes — tratar na Silver.
```

- [ ] **Step 4: Criar `docs/technical-context/data-catalog/bronze/customer_crm_level.md`**

```markdown
# Catálogo: bronze.customer_crm_level

**Descrição:** Histórico de níveis CRM mensais por cliente. Registros existem apenas
nos meses em que houve mudança de nível — meses sem registro devem receber o último
nível atribuído via forward-fill (aplicado na Silver).
**Camada:** Bronze
**Fonte:** Customer_crm_level.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| customer_id | TEXT | ID do cliente | Numérico como texto |
| date_yearmonth | TEXT | Mês de atribuição do nível (raw) | Formato a verificar após ingestão |
| crm_level | TEXT | Nível CRM atribuído | Verificar valores únicos após ingestão |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Regras de Negócio

- **RN-003 (forward-fill):** Registros existem apenas nos meses de mudança. Para meses
  intermediários, usar o nível mais recente. Aplicado na Silver.
- Exemplo: Bronze em Out/18 e Silver em Jan/19 → Nov/18 e Dez/18 são Bronze.

## Notas

- Não existe um registro para cada mês de cada cliente — isso é intencional.
- A tabela `silver.customer_crm_level` terá um registro por mês por cliente após o forward-fill.
```

- [ ] **Step 5: Criar `docs/technical-context/data-catalog/bronze/events.md`**

```markdown
# Catálogo: bronze.events

**Descrição:** Informações sobre os eventos esportivos disponíveis para apostas na temporada.
**Camada:** Bronze
**Fonte:** Events.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| event_id | TEXT | ID único do evento | Numérico como texto |
| event_sport_name | TEXT | Tipo de esporte | Verificar após ingestão (foco: Football) |
| event_class_name | TEXT | Classe do evento | Verificar após ingestão |
| event_type_name | TEXT | Tipo de liga | Verificar após ingestão (foco: Romanian Football) |
| event_name | TEXT | Nome do evento (ex: Time A vs Time B) | — |
| event_start_time | TEXT | Horário real de início do evento (raw) | — |
| event_end_time | TEXT | Horário real de término do evento (raw) | — |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Notas

- `event_start_time` é critical para a regra RN-002 (Live vs. Pre-event).
- O dataset pode conter eventos de outros esportes além do futebol romeno.
  Filtrar por `event_sport_name` e `event_type_name` quando necessário.
```

- [ ] **Step 6: Criar `docs/technical-context/data-catalog/bronze/sportsbook.md`**

```markdown
# Catálogo: bronze.sportsbook

**Descrição:** Registro de todas as apostas realizadas e liquidadas na temporada.
Esta é a tabela principal de atividade — fonte para os KPIs de Turnover, Winnings
e Gross Revenue.
**Camada:** Bronze
**Fonte:** Sportsbook.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| sportbetsettled_bet_id | TEXT | ID único da aposta | — |
| bettype_name | TEXT | Tipo de aposta | Verificar após ingestão |
| market_template_name | TEXT | Mercado da aposta (ex: Match Winner, Both Teams to Score) | Verificar após ingestão |
| sportbetsettled_customer_id | TEXT | ID do cliente que fez a aposta | Referência a bronze.customer |
| sportbetsettled_settled | TEXT | Timestamp de liquidação da aposta (raw) | — |
| sportbetsettled_placed | TEXT | Timestamp de colocação da aposta (raw) | — |
| channel_name | TEXT | Dispositivo/canal usado | Verificar após ingestão (Android, iOS, Web) |
| sportbetsettled_event_id | TEXT | ID do evento apostado | Referência a bronze.events |
| turnover | TEXT | Valor apostado em moeda local (raw) | Numérico como texto |
| winnings | TEXT | Ganhos do cliente em moeda local (raw) | Numérico como texto |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Regras de Negócio

- **RN-001 (Gross Revenue):** Calculado na Silver como `turnover - winnings`
- **RN-002 (Live vs. Pre-event):** `is_live = (placed_at >= event_start_time)`
  requer JOIN com `silver.events` para obter `event_start_time`

## Notas

- `turnover` e `winnings` são armazenados como TEXT na Bronze — converter para
  NUMERIC(12,2) na Silver.
- Uma aposta com `winnings = 0` significa que o cliente perdeu a aposta.
- `gross_revenue` positivo = casa ganhou; negativo = casa pagou mais do que recebeu.
```

- [ ] **Step 7: Criar `docs/technical-context/data-catalog/silver/README.md`**

```markdown
# Catálogo Silver — Em Construção

O catálogo das tabelas da camada Silver será populado no Plano 2,
quando as transformações forem implementadas.

Tabelas previstas:
- `silver.customer`
- `silver.customer_crm_level`
- `silver.events`
- `silver.sportsbook`
- `silver.cashouts`

Invocar skill `update-data-catalog` ao criar cada tabela Silver.
```

- [ ] **Step 8: Criar `docs/technical-context/data-catalog/gold/README.md`**

```markdown
# Catálogo Gold — Em Construção

O catálogo das tabelas da camada Gold será populado no Plano 2,
quando as agregações forem implementadas.

Tabelas previstas:
- `gold.customer_performance`
- `gold.customer_segments`
- `gold.betting_preferences`
- `gold.crm_performance`
- `gold.season_summary`
- `gold.cashout_analysis`

Invocar skill `update-data-catalog` ao criar cada tabela Gold.
```

- [ ] **Step 9: Commit**

```bash
git add docs/technical-context/data-catalog/
git commit -m "docs: criar catálogo de dados completo da camada Bronze"
```

---

## Task 16: Commit final, revisão e push para o GitHub

- [ ] **Step 1: Verificar status do repositório**

```bash
git status
git log --oneline
```

Saída esperada: todos os arquivos commitados, nenhuma mudança pendente.

- [ ] **Step 2: Verificar que o `.env` não está incluído**

```bash
git ls-files | grep ".env"
```

Saída esperada: apenas `.env.example` listado, nunca `.env`.

- [ ] **Step 3: Subir o ambiente completo para validação final**

```bash
docker compose up postgres -d
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('bronze','silver','gold') ORDER BY schema_name;"
```

Saída esperada:
```
 schema_name
-------------
 bronze
 gold
 silver
(3 rows)
```

- [ ] **Step 4: Contar tabelas por schema para verificação final**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "SELECT table_schema, COUNT(*) as total_tabelas FROM information_schema.tables WHERE table_schema IN ('bronze','silver','gold') GROUP BY table_schema ORDER BY table_schema;"
```

Saída esperada:
```
 table_schema | total_tabelas
--------------+---------------
 bronze       |             5
 gold         |             6
 silver       |             5
(3 rows)
```

- [ ] **Step 5: Parar containers**

```bash
docker compose down
```

- [ ] **Step 6: Push para o GitHub**

```bash
git push origin main
```

- [ ] **Step 7: Verificar repositório no GitHub**

Acessar `https://github.com/jurandircln/sportsbook-bi-analysis` e confirmar:
- Todos os arquivos presentes
- CLAUDE.md visível na raiz
- Estrutura de diretórios correta

---

## Resumo do que foi construído

Ao final deste plano, o repositório terá:

| Artefato | Quantidade |
|---|---|
| Schemas PostgreSQL | 3 (bronze, silver, gold) |
| Tabelas DDL | 16 (5 Bronze + 5 Silver + 6 Gold) |
| ADRs | 5 |
| Skills | 4 |
| Arquivos de catálogo de dados | 7 (5 Bronze + 2 README) |
| Documentos SDD | 9 (vision, personas, journeys, competitive, kpis, business-rules, glossary, stack, codebase-guide) |
| Arquivos Docker | 3 (docker-compose.yml, Dockerfile, docker/init.sql) |

**Próximo passo:** Plano 2 — Ingestão de dados (Bronze), transformações (Silver), agregações (Gold), dashboard Streamlit e agente Agno.
