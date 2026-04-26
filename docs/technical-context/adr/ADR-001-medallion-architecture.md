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
