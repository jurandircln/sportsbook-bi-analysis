# Catálogo: Camada Gold

**Descrição:** Métricas analíticas pré-calculadas prontas para consumo pelo dashboard e agente BI.
Todas as tabelas são reconstruídas a partir do zero a cada pipeline run (TRUNCATE + INSERT).
**Camada:** Gold
**Schema:** `gold`
**Dependências:** Requer Silver populada.

---

## gold.season_summary

**Descrição:** Resumo mensal da temporada — KPIs agregados por mês de Set/2018 a Ago/2019.

| Coluna | Tipo | Descrição |
|---|---|---|
| month | DATE | Primeiro dia do mês (ex: `2018-09-01`) |
| total_customers | INTEGER | Clientes com ao menos uma aposta no mês |
| new_customers | INTEGER | Clientes que apostaram pela primeira vez em toda a temporada neste mês |
| churned_customers | INTEGER | Clientes que apostaram em meses anteriores mas não neste (sempre 0 neste dataset) |
| total_bets | INTEGER | Total de apostas liquidadas no mês |
| total_turnover | NUMERIC(12,2) | Soma dos valores apostados no mês |
| total_winnings | NUMERIC(12,2) | Soma dos prêmios pagos no mês |
| gross_revenue | NUMERIC(12,2) | `turnover - winnings` — receita bruta da casa |
| live_bet_pct | NUMERIC(5,2) | Percentual de apostas live no mês (`live_bets / total_bets * 100`) |
| updated_at | TIMESTAMP | Momento da última atualização do registro |

---

## gold.customer_performance

**Descrição:** Performance acumulada de cada cliente durante toda a temporada.

| Coluna | Tipo | Descrição |
|---|---|---|
| customer_id | INTEGER | ID do cliente (PK) |
| gender | VARCHAR(20) | Gênero (`Male`, `Female`) |
| age | INTEGER | Idade calculada a partir de `customer_birthday` (NULL se data ausente) |
| total_bets | INTEGER | Total de apostas do cliente na temporada |
| total_turnover | NUMERIC(12,2) | Total apostado pelo cliente |
| total_winnings | NUMERIC(12,2) | Total de prêmios recebidos pelo cliente |
| gross_revenue | NUMERIC(12,2) | Receita bruta gerada pelo cliente (`turnover - winnings`) |
| live_bets | INTEGER | Número de apostas live |
| pre_event_bets | INTEGER | Número de apostas pré-evento |
| cashout_attempts | INTEGER | Total de tentativas de cash out do cliente |
| successful_cashouts | INTEGER | Cash outs bem-sucedidos do cliente |
| updated_at | TIMESTAMP | Momento da última atualização |

---

## gold.customer_segments

**Descrição:** Segmentação dos clientes por comportamento em relação à temporada analisada.

| Coluna | Tipo | Descrição |
|---|---|---|
| customer_id | INTEGER | ID do cliente (PK) |
| segment | VARCHAR(20) | Segmento do cliente (ver abaixo) |
| first_bet_date | DATE | Data da primeira aposta do cliente em toda a base |
| last_bet_date | DATE | Data da última aposta do cliente em toda a base |
| crm_level | VARCHAR(20) | Nível CRM mais recente do cliente (`Bronze`, `Silver`, `Gold`, `Platinum`, `Diamond`) |
| updated_at | TIMESTAMP | Momento da última atualização |

**Valores de `segment`:**

| Valor | Definição |
|---|---|
| `novo` | Apostou apenas durante a temporada Set/2018–Ago/2019 (sem histórico pré-temporada) |
| `existente` | Apostou antes E durante a temporada |
| `saindo` | Apostou antes da temporada mas não durante ela |

---

## gold.betting_preferences

**Descrição:** Preferências de apostas por cliente — canal, mercado, tipo e horário de pico.

| Coluna | Tipo | Descrição |
|---|---|---|
| customer_id | INTEGER | ID do cliente (PK) |
| preferred_channel | VARCHAR(50) | Canal com maior número de apostas (`Android`, `iOS`, `Mobile`, `Internet`) |
| preferred_market | VARCHAR(100) | Mercado com maior número de apostas (ex: `Match Winner`) |
| preferred_bet_type | VARCHAR(50) | Tipo de aposta preferido (ex: `Single`) |
| live_bet_pct | NUMERIC(5,2) | Percentual de apostas live do cliente |
| peak_hour | INTEGER | Hora do dia (0–23) com maior volume de apostas do cliente |
| updated_at | TIMESTAMP | Momento da última atualização |

---

## gold.crm_performance

**Descrição:** Métricas agregadas por nível CRM — permite comparar o valor de cada segmento.

| Coluna | Tipo | Descrição |
|---|---|---|
| crm_level | VARCHAR(20) | Nível CRM (PK) — `Bronze`, `Silver`, `Gold`, `Platinum`, `Diamond` |
| customer_count | INTEGER | Número de clientes com esse nível CRM |
| total_bets | INTEGER | Total de apostas de clientes do nível |
| total_turnover | NUMERIC(12,2) | Turnover agregado do nível |
| total_winnings | NUMERIC(12,2) | Winnings agregados do nível |
| gross_revenue | NUMERIC(12,2) | Gross revenue agregado do nível |
| avg_bets_per_customer | NUMERIC(10,2) | Média de apostas por cliente |
| avg_turnover_per_customer | NUMERIC(12,2) | Média de turnover por cliente |
| avg_gross_revenue_per_customer | NUMERIC(12,2) | Média de gross revenue por cliente |
| updated_at | TIMESTAMP | Momento da última atualização |

**Ordem de valor dos níveis:** Bronze < Silver < Gold < Platinum < Diamond

---

## gold.cashout_analysis

**Descrição:** Análise mensal do uso do Cash Out — volume, taxa de sucesso e valores.

| Coluna | Tipo | Descrição |
|---|---|---|
| month | DATE | Primeiro dia do mês (PK) |
| total_attempts | INTEGER | Total de tentativas de cash out no mês |
| successful_attempts | INTEGER | Tentativas bem-sucedidas |
| failed_attempts | INTEGER | Tentativas malsucedidas |
| success_rate | NUMERIC(5,2) | Taxa de sucesso (`successful / total * 100`) |
| total_cashout_amount | NUMERIC(12,2) | Soma dos valores de cash out realizados com sucesso |
| avg_cashout_amount | NUMERIC(12,2) | Valor médio por cash out bem-sucedido |
| updated_at | TIMESTAMP | Momento da última atualização |

## Notas Gerais

- Todas as tabelas Gold são reconstruídas integralmente a cada pipeline run.
- Valores monetários em moeda local da operação (RON — leu romeno).
- `gross_revenue` positivo indica receita para a casa; negativo indica pagamento maior que receita.
- Cash Out é uma funcionalidade nova na temporada 2018/19 — primeiro ciclo de dados disponíveis.
