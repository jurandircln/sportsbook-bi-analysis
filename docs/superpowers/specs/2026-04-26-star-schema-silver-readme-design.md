# Design: Star Schema na Silver + README do Projeto

**Data:** 2026-04-26
**Status:** Aprovado
**Repositório:** https://github.com/jurandircln/sportsbook-bi-analysis

---

## 1. Contexto e Motivação

A camada Silver foi inicialmente modelada com tabelas planas (flat tables). Esta spec
documenta a refatoração para **Star Schema (Kimball)**, tornando a Silver uma camada
dimensional com separação explícita entre tabelas fato e dimensão. Também documenta
a criação do README.md do projeto no padrão focado em valor de negócio.

**Escopo desta spec:**
- Substituir 5 DDLs Silver flat por 8 DDLs com nomenclatura `fact_*` / `dim_*`
- Atualizar `docker/init.sql` para refletir o novo schema
- Criar ADR-006 (Star Schema) e atualizar ADR-002 (status parcialmente substituído)
- Atualizar skill `db-modeling` com templates e checklist de Star Schema
- Criar `README.md` com foco em valor de negócio

---

## 2. Star Schema — Camada Silver

### 2.1 Tabelas Fato

#### `silver.fact_bets`
Grão: uma linha por aposta liquidada.

| Coluna | Tipo | Descrição |
|---|---|---|
| bet_id | TEXT PK | ID único da aposta |
| customer_id | INTEGER NOT NULL | FK → silver.dim_customer |
| event_id | INTEGER | FK → silver.dim_event |
| date_id | INTEGER NOT NULL | FK → silver.dim_date (formato YYYYMMDD da placed_at) |
| market_id | INTEGER | FK → silver.dim_market |
| channel_id | INTEGER | FK → silver.dim_channel |
| placed_at | TIMESTAMP NOT NULL | Timestamp completo da aposta (para análises intra-dia) |
| settled_at | TIMESTAMP | Timestamp de liquidação |
| placed_hour | INTEGER | Hora do dia da aposta (0–23) — dimensão degenerada |
| turnover | NUMERIC(12,2) NOT NULL | Valor apostado |
| winnings | NUMERIC(12,2) NOT NULL | Ganhos do cliente |
| gross_revenue | NUMERIC(12,2) NOT NULL | Receita bruta = turnover - winnings |
| is_live | BOOLEAN NOT NULL | TRUE se aposta feita após início do evento |
| ingested_at | TIMESTAMP | Controle de ingestão |

**Índices:** customer_id, event_id, date_id, placed_at

#### `silver.fact_cashouts`
Grão: uma linha por tentativa de cash out.

| Coluna | Tipo | Descrição |
|---|---|---|
| cashout_id | TEXT PK | ID único da tentativa |
| bet_id | TEXT NOT NULL | Dimensão degenerada — referência à aposta |
| date_id | INTEGER NOT NULL | FK → silver.dim_date (data da tentativa) |
| created_at | TIMESTAMP NOT NULL | Timestamp da tentativa |
| status | VARCHAR(50) NOT NULL | Resultado — dimensão degenerada (ex: Success, Failed) |
| cashout_amount | NUMERIC(12,2) | Valor solicitado |
| ingested_at | TIMESTAMP | Controle de ingestão |

**Índices:** bet_id, date_id

---

### 2.2 Tabelas Dimensão

#### `silver.dim_customer`
| Coluna | Tipo | Descrição |
|---|---|---|
| customer_id | INTEGER PK | ID natural do cliente |
| registration_date | DATE NOT NULL | Data de cadastro na plataforma |
| gender | VARCHAR(20) | Gênero |
| birth_date | DATE | Data de nascimento |
| age | INTEGER | Idade calculada no momento da análise |
| ingested_at | TIMESTAMP | Controle de ingestão |

#### `silver.dim_event`
| Coluna | Tipo | Descrição |
|---|---|---|
| event_id | INTEGER PK | ID natural do evento |
| sport_name | VARCHAR(100) | Tipo de esporte |
| class_name | VARCHAR(100) | Classe do evento |
| type_name | VARCHAR(100) | Tipo de liga |
| event_name | VARCHAR(255) | Nome do evento |
| start_time | TIMESTAMP | Horário de início |
| end_time | TIMESTAMP | Horário de término |
| ingested_at | TIMESTAMP | Controle de ingestão |

#### `silver.dim_date`
Granularidade: um registro por dia. Gerada durante a transformação cobrindo todo o
período relevante (com margem antes e depois da temporada).

| Coluna | Tipo | Descrição |
|---|---|---|
| date_id | INTEGER PK | Chave no formato YYYYMMDD (ex: 20180901) |
| full_date | DATE NOT NULL | Data completa |
| year | INTEGER | Ano (2018 ou 2019) |
| month | INTEGER | Mês (1–12) |
| month_name | VARCHAR(20) | Nome do mês em português |
| day | INTEGER | Dia do mês (1–31) |
| day_of_week | INTEGER | Dia da semana (1=Segunda, 7=Domingo) |
| day_name | VARCHAR(20) | Nome do dia em português |
| is_weekend | BOOLEAN | TRUE para Sábado e Domingo |
| ingested_at | TIMESTAMP | Controle de ingestão |

> `placed_hour` permanece em `fact_bets` como dimensão degenerada para não inflar
> `dim_date` com granularidade de hora.

#### `silver.dim_market`
Surrogate key — dedupado por combinação única de mercado + tipo de aposta.

| Coluna | Tipo | Descrição |
|---|---|---|
| market_id | SERIAL PK | Chave substituta |
| market_name | VARCHAR(100) NOT NULL | Nome do mercado (ex: Match Winner) |
| bet_type | VARCHAR(100) | Tipo de aposta |
| ingested_at | TIMESTAMP | Controle de ingestão |

#### `silver.dim_channel`
Surrogate key — dedupado por nome do canal.

| Coluna | Tipo | Descrição |
|---|---|---|
| channel_id | SERIAL PK | Chave substituta |
| channel_name | VARCHAR(50) NOT NULL | Canal (ex: Android, iOS, Web) |
| ingested_at | TIMESTAMP | Controle de ingestão |

#### `silver.dim_crm_level`
Dimensão com variação temporal — um registro por cliente por mês, após forward-fill.

| Coluna | Tipo | Descrição |
|---|---|---|
| customer_id | INTEGER NOT NULL | ID do cliente |
| year_month | DATE NOT NULL | Primeiro dia do mês (ex: 2018-10-01) |
| crm_level | VARCHAR(50) NOT NULL | Nível CRM após forward-fill |
| ingested_at | TIMESTAMP | Controle de ingestão |
| **PK** | **(customer_id, year_month)** | — |

Para consultas de análise por CRM: JOIN via `customer_id` + truncamento de `placed_at`
para o mês correspondente em `dim_crm_level`.

---

### 2.3 Mapeamento de Arquivos DDL Silver

| Arquivo atual (removido) | Arquivo novo |
|---|---|
| `002_create_customer.sql` | `002_create_dim_customer.sql` |
| `003_create_customer_crm_level.sql` | `003_create_dim_crm_level.sql` |
| `004_create_events.sql` | `004_create_dim_event.sql` |
| `005_create_sportsbook.sql` | `005_create_dim_market.sql` + `006_create_dim_channel.sql` + `007_create_dim_date.sql` + `008_create_fact_bets.sql` |
| `006_create_cashouts.sql` | `009_create_fact_cashouts.sql` |

> `sql/silver/001_create_schema.sql` permanece sem alteração.

`docker/init.sql` deve ser regenerado refletindo os novos DDLs na ordem correta
(dimensões antes das fatos, para que FKs sejam válidas).

---

## 3. ADR-006 — Adoção de Star Schema na Silver

**Arquivo:** `docs/technical-context/adr/ADR-006-star-schema-silver.md`

**Conteúdo:**

```markdown
# ADR-006: Adoção de Star Schema na Camada Silver

**Data:** 2026-04-26
**Status:** Aceita
**Substitui parcialmente:** ADR-002 (seção "Camada Silver")

## Contexto

A modelagem inicial da Silver (ADR-002) usava tabelas planas sem distinção entre
entidades analíticas. Para suportar queries analíticas eficientes no dashboard e no
agente de BI, e para tornar explícita a separação entre medidas e atributos, é
necessário um modelo dimensional estruturado.

## Decisão

Adotar Star Schema (Kimball) na camada Silver com:
- Tabelas fato: fact_bets, fact_cashouts
- Tabelas dimensão: dim_customer, dim_event, dim_date, dim_market, dim_channel, dim_crm_level

dim_crm_level mantida como dimensão separada com granularidade mensal (Option B),
referenciada via JOIN por customer_id + mês truncado da aposta.

dim_date com granularidade de dia; placed_hour mantido em fact_bets como
dimensão degenerada para análise de horário de pico sem inflar a dimensão.

dim_market e dim_channel usam surrogate key (SERIAL) pois os valores originais
são texto livre sem garantia de unicidade estável.

## Consequências

Queries analíticas no dashboard e no agente ficam mais expressivas e performáticas.
O modelo é autodocumentado — fatos têm medidas, dimensões têm atributos.
A transformação Bronze→Silver fica ligeiramente mais complexa (dedupagem de dim_market
e dim_channel, geração de dim_date). Aceita-se esse custo em troca de um modelo
analítico robusto e escalável.
```

**Atualização do ADR-002:** linha do status muda para:
```
**Status:** Aceita (seção Silver parcialmente substituída por ADR-006)
```

---

## 4. Skill db-modeling — Atualização

**Novos itens no checklist:**
```
- [ ] Em tabelas Silver, identificar se a tabela é FATO ou DIMENSÃO (Star Schema — ADR-006)
- [ ] Tabelas fato: nomenclatura silver.fact_<nome>, incluir medidas e FKs para dimensões
- [ ] Tabelas dimensão: nomenclatura silver.dim_<nome>
      - Usar chave natural (INTEGER) quando o ID original é estável
      - Usar surrogate key (SERIAL) quando o valor original é texto livre
- [ ] dim_date: não duplicar — verificar se o período já está coberto antes de recriar
- [ ] FKs em fact_*: criar índices em todas as colunas de FK
```

**Novos templates adicionados à skill:**

```sql
-- Template: Tabela Fato (Silver)
-- Regras de negócio aplicadas: <listar>
-- Fonte: bronze.<origem>
CREATE TABLE IF NOT EXISTS silver.fact_<nome> (
    <id>            TEXT         PRIMARY KEY,
    <dim_fk>_id     INTEGER      NOT NULL,    -- FK → silver.dim_<nome>
    <medida>        NUMERIC(12,2) NOT NULL,
    <dim_degenera>  VARCHAR(N),               -- dimensão degenerada (sem tabela própria)
    ingested_at     TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_silver_fact_<nome>_<dim>
    ON silver.fact_<nome> (<dim_fk>_id);
```

```sql
-- Template: Tabela Dimensão (Silver) — chave natural
-- Fonte: bronze.<origem>
CREATE TABLE IF NOT EXISTS silver.dim_<nome> (
    <natural_id>    INTEGER      PRIMARY KEY,
    <atributo_1>    VARCHAR(N),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

-- Template: Tabela Dimensão (Silver) — surrogate key
CREATE TABLE IF NOT EXISTS silver.dim_<nome> (
    <surrogate_id>  SERIAL       PRIMARY KEY,
    <atributo_1>    VARCHAR(N)   NOT NULL,
    ingested_at     TIMESTAMP DEFAULT NOW()
);
```

---

## 5. README.md

**Arquivo:** `README.md` (raiz do repositório)

**Estrutura:**

```markdown
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
```

---

## 6. Resumo dos Artefatos

| Artefato | Ação | Localização |
|---|---|---|
| 5 DDLs Silver (flat) | Substituídos por 8 DDLs (fact/dim) | `sql/silver/` |
| `docker/init.sql` | Regenerado com novos DDLs | `docker/init.sql` |
| ADR-006 | Criado | `docs/technical-context/adr/ADR-006-star-schema-silver.md` |
| ADR-002 | Status atualizado | `docs/technical-context/adr/ADR-002-database-modeling.md` |
| Skill db-modeling | Atualizada com templates fact/dim | `.claude/skills/db-modeling.md` |
| README.md | Criado do zero | `README.md` |
