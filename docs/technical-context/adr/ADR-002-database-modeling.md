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
