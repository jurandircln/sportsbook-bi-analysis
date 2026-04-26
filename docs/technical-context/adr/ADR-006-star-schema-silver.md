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
