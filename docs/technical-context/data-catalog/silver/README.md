# Catálogo de Dados — Camada Silver (Star Schema)

**Atualizado em:** 2026-04-26
**Modelo:** Star Schema (Kimball) — ADR-006

A camada Silver contém dados tipados com regras de negócio aplicadas, organizados em Star Schema.

## Tabelas Dimensão

| Tabela | Chave | Fonte Bronze | Descrição |
|---|---|---|---|
| `silver.dim_customer` | `customer_id` (INTEGER, natural) | `bronze.customer` | Clientes cadastrados |
| `silver.dim_crm_level` | `(customer_id, year_month)` (composta) | `bronze.customer_crm_level` | Nível CRM mensal com forward-fill |
| `silver.dim_event` | `event_id` (INTEGER, natural) | `bronze.events` | Eventos esportivos |
| `silver.dim_market` | `market_id` (SERIAL, surrogate) | `bronze.sportsbook` | Mercados de aposta dedupados |
| `silver.dim_channel` | `channel_id` (SERIAL, surrogate) | `bronze.sportsbook` | Canais de aposta dedupados |
| `silver.dim_date` | `date_id` (INTEGER YYYYMMDD) | Gerada na transformação | Calendário por dia |

## Tabelas Fato

| Tabela | Chave | Grão | Fonte Bronze |
|---|---|---|---|
| `silver.fact_bets` | `bet_id` (TEXT) | 1 linha por aposta liquidada | `bronze.sportsbook` + `silver.dim_event` |
| `silver.fact_cashouts` | `cashout_id` (TEXT) | 1 linha por tentativa de cash out | `bronze.cashouts` |

## Regras de Negócio Aplicadas

- `fact_bets.gross_revenue = turnover - winnings`
- `fact_bets.is_live = placed_at >= event_start_time` (via JOIN com dim_event)
- `fact_bets.placed_hour = EXTRACT(HOUR FROM placed_at)` (dimensão degenerada)
- `dim_crm_level`: forward-fill — meses sem registro usam o nível mais recente
- `dim_market` e `dim_channel`: dedupados por valor único na transformação

## Detalhes por Tabela

### silver.dim_customer

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| customer_id | INTEGER | NOT NULL | ID do cliente (PK, chave natural) |
| registration_date | DATE | NOT NULL | Data de cadastro |
| gender | VARCHAR(20) | NULL | Gênero |
| birth_date | DATE | NULL | Data de nascimento |
| age | INTEGER | NULL | Idade calculada |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.dim_crm_level

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| customer_id | INTEGER | NOT NULL | ID do cliente (PK parte 1) |
| year_month | DATE | NOT NULL | Primeiro dia do mês (PK parte 2) |
| crm_level | VARCHAR(50) | NOT NULL | Nível CRM após forward-fill |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.dim_event

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| event_id | INTEGER | NOT NULL | ID do evento (PK, chave natural) |
| sport_name | VARCHAR(100) | NULL | Tipo de esporte |
| class_name | VARCHAR(100) | NULL | Classe do evento |
| type_name | VARCHAR(100) | NULL | Tipo de liga |
| event_name | VARCHAR(255) | NULL | Nome do evento |
| start_time | TIMESTAMP | NULL | Horário de início (usado para is_live) |
| end_time | TIMESTAMP | NULL | Horário de término |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.dim_market

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| market_id | SERIAL | NOT NULL | ID surrogate (PK) |
| market_name | VARCHAR(100) | NOT NULL | Nome do mercado |
| bet_type | VARCHAR(100) | NULL | Tipo de aposta |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.dim_channel

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| channel_id | SERIAL | NOT NULL | ID surrogate (PK) |
| channel_name | VARCHAR(50) | NOT NULL | Nome do canal (Android, iOS, Web, etc.) |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.dim_date

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| date_id | INTEGER | NOT NULL | Data como YYYYMMDD (PK) |
| full_date | DATE | NOT NULL | Data completa |
| year | INTEGER | NOT NULL | Ano |
| month | INTEGER | NOT NULL | Mês (1–12) |
| month_name | VARCHAR(20) | NOT NULL | Nome do mês em português |
| day | INTEGER | NOT NULL | Dia do mês |
| day_of_week | INTEGER | NOT NULL | Dia da semana (1=Segunda, 7=Domingo) |
| day_name | VARCHAR(20) | NOT NULL | Nome do dia em português |
| is_weekend | BOOLEAN | NOT NULL | TRUE para Sábado e Domingo |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.fact_bets

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| bet_id | TEXT | NOT NULL | ID da aposta (PK) |
| customer_id | INTEGER | NOT NULL | FK → dim_customer |
| event_id | INTEGER | NULL | FK → dim_event |
| date_id | INTEGER | NOT NULL | FK → dim_date (YYYYMMDD) |
| market_id | INTEGER | NULL | FK → dim_market |
| channel_id | INTEGER | NULL | FK → dim_channel |
| placed_at | TIMESTAMP | NOT NULL | Timestamp da aposta |
| settled_at | TIMESTAMP | NULL | Timestamp de liquidação |
| placed_hour | INTEGER | NULL | Hora do dia (0–23) — dimensão degenerada |
| turnover | NUMERIC(12,2) | NOT NULL | Valor apostado |
| winnings | NUMERIC(12,2) | NOT NULL | Ganhos do cliente |
| gross_revenue | NUMERIC(12,2) | NOT NULL | Receita bruta = turnover - winnings |
| is_live | BOOLEAN | NOT NULL | TRUE se aposta feita após início do evento |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |

### silver.fact_cashouts

| Coluna | Tipo | Nulo | Descrição |
|---|---|---|---|
| cashout_id | TEXT | NOT NULL | ID da tentativa (PK) |
| bet_id | TEXT | NOT NULL | ID da aposta referenciada (dim degenerada) |
| date_id | INTEGER | NOT NULL | FK → dim_date (YYYYMMDD) |
| created_at | TIMESTAMP | NOT NULL | Timestamp da tentativa |
| status | VARCHAR(50) | NOT NULL | Resultado (Success, Failed etc.) — dim degenerada |
| cashout_amount | NUMERIC(12,2) | NULL | Valor solicitado |
| ingested_at | TIMESTAMP | NOT NULL | Timestamp de ingestão |
