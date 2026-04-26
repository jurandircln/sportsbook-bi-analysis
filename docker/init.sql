-- =============================================================================
-- SCRIPT DE INICIALIZAÇÃO DO BANCO DE DADOS
-- Projeto: Sportsbook BI Analysis — Temporada Futebol Romeno 2018/19
-- Executa automaticamente ao subir o container PostgreSQL
-- Cria schemas e tabelas nas 3 camadas: Bronze, Silver, Gold
-- =============================================================================


-- =============================================================================
-- CAMADA BRONZE
-- Dados brutos ingeridos diretamente dos CSVs, sem transformação
-- Todas as colunas em TEXT para preservar o dado original sem risco de cast
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS bronze;

-- Tabela Bronze: tentativas de cash out
-- Fonte: Cashouts.csv
CREATE TABLE IF NOT EXISTS bronze.cashouts (
    cashout_attempt_bet_id              TEXT,
    cashout_attempt_bet_cashout_id      TEXT,
    cashout_attempt_bet_cashout_created TEXT,
    cashout_attempt_bet_cashout_status  TEXT,
    cashout_attempt_cashout_amount      TEXT,
    ingested_at                         TIMESTAMP DEFAULT NOW()
);

-- Tabela Bronze: base de clientes
-- Fonte: Customer.csv
CREATE TABLE IF NOT EXISTS bronze.customer (
    customer_id              TEXT,
    customer_datecreation_id TEXT,
    customer_gender_name     TEXT,
    customer_birthday        TEXT,
    ingested_at              TIMESTAMP DEFAULT NOW()
);

-- Tabela Bronze: níveis CRM mensais por cliente
-- Fonte: Customer_crm_level.csv
-- ATENÇÃO: registros existem apenas nos meses de mudança de nível.
-- Para meses intermediários, aplicar forward-fill na camada Silver.
CREATE TABLE IF NOT EXISTS bronze.customer_crm_level (
    customer_id    TEXT,
    date_yearmonth TEXT,
    crm_level      TEXT,
    ingested_at    TIMESTAMP DEFAULT NOW()
);

-- Tabela Bronze: informações de eventos esportivos
-- Fonte: Events.csv
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

-- Tabela Bronze: atividade de apostas
-- Fonte: Sportsbook.csv
-- KPI principal: Gross Revenue = Turnover - Winnings (calculado na Silver)
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


-- =============================================================================
-- CAMADA SILVER — Star Schema (Kimball)
-- Dados limpos, tipados e com regras de negócio aplicadas
-- Estrutura: tabelas dimensão (dim_*) seguidas de tabelas fato (fact_*)
-- Dimensões devem ser criadas antes dos fatos (FKs lógicas)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- Dimensão: cliente
-- Chave natural: customer_id (INTEGER estável)
-- Fonte: bronze.customer
CREATE TABLE IF NOT EXISTS silver.dim_customer (
    customer_id        INTEGER   PRIMARY KEY,
    registration_date  DATE      NOT NULL,
    gender             VARCHAR(20),
    birth_date         DATE,
    age                INTEGER,
    ingested_at        TIMESTAMP DEFAULT NOW()
);

-- Dimensão: nível CRM por cliente por mês (variação temporal)
-- Regra de negócio: forward-fill aplicado — meses sem registro usam o nível mais recente.
-- Para JOIN na análise: customer_id + DATE_TRUNC('month', placed_at) = year_month
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.dim_crm_level (
    customer_id  INTEGER     NOT NULL,
    year_month   DATE        NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_customer
    ON silver.dim_crm_level (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_month
    ON silver.dim_crm_level (year_month);

-- Dimensão: evento esportivo
-- Chave natural: event_id (INTEGER estável)
-- Fonte: bronze.events
CREATE TABLE IF NOT EXISTS silver.dim_event (
    event_id    INTEGER      PRIMARY KEY,
    sport_name  VARCHAR(100),
    class_name  VARCHAR(100),
    type_name   VARCHAR(100),
    event_name  VARCHAR(255),
    start_time  TIMESTAMP,
    end_time    TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Dimensão: mercado de aposta
-- Surrogate key (SERIAL): valores originais são texto livre sem unicidade garantida.
-- Dedupado por combinação única de (market_name, bet_type) na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_market (
    market_id    SERIAL       PRIMARY KEY,
    market_name  VARCHAR(100) NOT NULL,
    bet_type     VARCHAR(100),
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_market_unique
    ON silver.dim_market (market_name, bet_type);

-- Dimensão: canal de aposta
-- Surrogate key (SERIAL): valores originais são texto livre.
-- Dedupado por channel_name na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_channel (
    channel_id    SERIAL      PRIMARY KEY,
    channel_name  VARCHAR(50) NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_channel_unique
    ON silver.dim_channel (channel_name);

-- Dimensão: calendário por dia
-- Granularidade: 1 registro por dia. Gerada na transformação cobrindo o período
-- relevante (Jul/2017 a Set/2019, com margem para apostas pré-temporada).
-- Chave: YYYYMMDD como INTEGER (ex: 20180901).
-- placed_hour permanece em fact_bets como dimensão degenerada (não infla esta tabela).
-- Fonte: gerada programaticamente durante a transformação
CREATE TABLE IF NOT EXISTS silver.dim_date (
    date_id      INTEGER     PRIMARY KEY,
    full_date    DATE        NOT NULL,
    year         INTEGER     NOT NULL,
    month        INTEGER     NOT NULL,
    month_name   VARCHAR(20) NOT NULL,
    day          INTEGER     NOT NULL,
    day_of_week  INTEGER     NOT NULL,
    day_name     VARCHAR(20) NOT NULL,
    is_weekend   BOOLEAN     NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_date_full_date
    ON silver.dim_date (full_date);

-- Fato: apostas liquidadas
-- Grão: 1 linha por aposta
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (via JOIN com dim_event na transformação)
--   placed_hour: dimensão degenerada (EXTRACT(HOUR FROM placed_at))
-- Fonte: bronze.sportsbook + silver.dim_event (para is_live)
CREATE TABLE IF NOT EXISTS silver.fact_bets (
    bet_id        TEXT          PRIMARY KEY,
    customer_id   INTEGER       NOT NULL,
    event_id      INTEGER,
    date_id       INTEGER       NOT NULL,
    market_id     INTEGER,
    channel_id    INTEGER,
    placed_at     TIMESTAMP     NOT NULL,
    settled_at    TIMESTAMP,
    placed_hour   INTEGER,
    turnover      NUMERIC(12,2) NOT NULL,
    winnings      NUMERIC(12,2) NOT NULL,
    gross_revenue NUMERIC(12,2) NOT NULL,
    is_live       BOOLEAN       NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_customer
    ON silver.fact_bets (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_event
    ON silver.fact_bets (event_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_date
    ON silver.fact_bets (date_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_placed_at
    ON silver.fact_bets (placed_at);

-- Fato: tentativas de cash out
-- Grão: 1 linha por tentativa de cash out
-- bet_id e status são dimensões degeneradas (sem tabela própria).
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.fact_cashouts (
    cashout_id      TEXT          PRIMARY KEY,
    bet_id          TEXT          NOT NULL,
    date_id         INTEGER       NOT NULL,
    created_at      TIMESTAMP     NOT NULL,
    status          VARCHAR(50)   NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_bet
    ON silver.fact_cashouts (bet_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_date
    ON silver.fact_cashouts (date_id);


-- =============================================================================
-- CAMADA GOLD
-- Tabelas analíticas desnormalizadas, prontas para consumo pelo dashboard e agente
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- Tabela Gold: KPIs de performance por cliente na temporada
-- Consumida por: dashboard (visão de clientes), agente (perguntas de performance)
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

-- Tabela Gold: segmentação dos clientes na temporada
-- Segmentos:
--   novo       = primeira aposta ocorreu durante a temporada (Set/2018–Ago/2019)
--   existente  = apostas antes E durante a temporada
--   saindo     = apostas antes da temporada, sem apostas nos últimos 3 meses dela
-- Consumida por: dashboard (comportamento da base), agente (perguntas de segmentação)
CREATE TABLE IF NOT EXISTS gold.customer_segments (
    customer_id     INTEGER PRIMARY KEY,
    segment         VARCHAR(20) NOT NULL,
    first_bet_date  DATE,
    last_bet_date   DATE,
    crm_level       VARCHAR(50),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Tabela Gold: preferências de aposta por cliente
-- Consumida por: dashboard (preferências), agente (perguntas de comportamento)
CREATE TABLE IF NOT EXISTS gold.betting_preferences (
    customer_id          INTEGER PRIMARY KEY,
    preferred_channel    VARCHAR(50),
    preferred_market     VARCHAR(100),
    preferred_bet_type   VARCHAR(100),
    live_bet_pct         NUMERIC(5,2),
    peak_hour            INTEGER,
    updated_at           TIMESTAMP DEFAULT NOW()
);

-- Tabela Gold: performance agregada por nível CRM
-- Consumida por: dashboard (visão por CRM), agente (perguntas por nível)
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

-- Tabela Gold: resumo mensal da temporada
-- Granularidade: 1 linha por mês da temporada (Set/2018 a Ago/2019)
-- Consumida por: dashboard (evolução temporal), agente (visão geral da temporada)
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

-- Tabela Gold: análise mensal de adoção e performance do cash out
-- Cash out foi funcionalidade nova introduzida na temporada
-- Consumida por: dashboard (análise de cash out), agente
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
