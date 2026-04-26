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
-- CAMADA SILVER
-- Dados limpos, tipados e com regras de negócio aplicadas
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- Tabela Silver: clientes com tipos corretos e idade calculada
-- Fonte: bronze.customer
CREATE TABLE IF NOT EXISTS silver.customer (
    customer_id        INTEGER PRIMARY KEY,
    registration_date  DATE NOT NULL,
    gender             VARCHAR(20),
    birth_date         DATE,
    age                INTEGER,
    ingested_at        TIMESTAMP DEFAULT NOW()
);

-- Tabela Silver: níveis CRM mensais com forward-fill aplicado
-- Regra de negócio: para meses sem registro, usar o nível mais recente atribuído.
-- Exemplo: Bronze em Out/18 e Silver em Jan/19 → Nov e Dez/18 são Bronze.
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.customer_crm_level (
    customer_id  INTEGER     NOT NULL,
    year_month   DATE        NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);

-- Tabela Silver: eventos com tipos corretos
-- Fonte: bronze.events
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

-- Tabela Silver: apostas com tipos corretos, gross revenue e flag live
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (aposta feita após início do evento)
-- Fonte: bronze.sportsbook + silver.events (para event_start_time)
CREATE TABLE IF NOT EXISTS silver.sportsbook (
    bet_id         TEXT          PRIMARY KEY,
    bet_type       VARCHAR(100),
    market         VARCHAR(100),
    customer_id    INTEGER       NOT NULL,
    settled_at     TIMESTAMP,
    placed_at      TIMESTAMP     NOT NULL,
    channel        VARCHAR(50),
    event_id       INTEGER,
    turnover       NUMERIC(12,2) NOT NULL,
    winnings       NUMERIC(12,2) NOT NULL,
    gross_revenue  NUMERIC(12,2) NOT NULL,
    is_live        BOOLEAN       NOT NULL,
    ingested_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_customer
    ON silver.sportsbook (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_placed_at
    ON silver.sportsbook (placed_at);
CREATE INDEX IF NOT EXISTS idx_silver_sportsbook_event
    ON silver.sportsbook (event_id);

-- Tabela Silver: tentativas de cash out com tipos corretos
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.cashouts (
    bet_id          TEXT          NOT NULL,
    cashout_id      TEXT          PRIMARY KEY,
    created_at      TIMESTAMP     NOT NULL,
    status          VARCHAR(50)   NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_cashouts_bet
    ON silver.cashouts (bet_id);


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
