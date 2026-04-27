# Design: Atualização do Catálogo de Dados Pós-Ingestão

**Data:** 2026-04-27
**Status:** Aprovado

## Contexto

Após a ingestão dos dados históricos e a execução completa do pipeline Bronze → Silver → Gold,
os arquivos do catálogo de dados contêm campos com valores ainda não verificados
("Verificar após ingestão"). O objetivo é substituir todos esses placeholders pelos
valores reais observados nos dados.

## Escopo

### Bronze — campos atualizados

| Arquivo | Campo | Valor anterior | Valor atual |
|---|---|---|---|
| `cashouts.md` | `cashout_attempt_bet_cashout_status` | Verificar valores únicos após ingestão | `` `Successful`, `Unsuccessful` `` |
| `customer.md` | `customer_gender_name` | Verificar após ingestão | `` `Male`, `Female` `` |
| `customer_crm_level.md` | `date_yearmonth` | Formato a verificar após ingestão | Inteiro YYYYMM, 201809–201908 |
| `customer_crm_level.md` | `crm_level` | Verificar valores únicos após ingestão | `Bronze`, `Silver`, `Gold`, `Platinum`, `Diamond` |
| `events.md` | `event_sport_name` | Verificar após ingestão (foco: Football) | `Soccer` (único valor) |
| `events.md` | `event_class_name` | Verificar após ingestão | `England`, `Germany`, `Greece`, `Italy`, `Romania`, `Spain` |
| `events.md` | `event_type_name` | Verificar após ingestão | `Liga 1`, `Premier League`, `LaLiga`, `Bundesliga`, `Serie A`, `Super League 1` e outras |
| `sportsbook.md` | `bettype_name` | Verificar após ingestão | `Single` (único valor) |
| `sportsbook.md` | `market_template_name` | Verificar após ingestão | 379 valores distintos — principais listados |
| `sportsbook.md` | `channel_name` | Verificar após ingestão | `Android`, `iOS`, `Mobile`, `Internet` |

### Gold — documentação completa

O arquivo `gold/README.md` foi reescrito do zero substituindo o placeholder "Em Construção"
pela documentação completa das 6 tabelas Gold:
- `gold.season_summary`
- `gold.customer_performance`
- `gold.customer_segments`
- `gold.betting_preferences`
- `gold.crm_performance`
- `gold.cashout_analysis`

Cada tabela documenta: descrição, colunas (nome, tipo, descrição), valores possíveis e notas.

### overview.md

Atualizado para refletir que Bronze (5 tabelas), Silver (Star Schema) e Gold (6 tabelas)
estão todos documentados.

## Decisões

- O mesmo nível de detalhe do catálogo Silver foi adotado para o Gold (padrão aprovado pelo usuário).
- Valores monetários documentados como RON (leu romeno).
- `bettype_name = Single` como único valor documenta uma limitação real do dataset,
  não uma omissão — importante para análises futuras.
- 379 mercados distintos no `market_template_name` — documentado apenas os top-5 para
  legibilidade; o analista deve consultar o banco para a lista completa.
