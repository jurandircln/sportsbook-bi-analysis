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
