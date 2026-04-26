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
