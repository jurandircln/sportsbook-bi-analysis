# Catálogo: bronze.cashouts

**Descrição:** Tentativas de uso da funcionalidade Cash Out por clientes apostadores.
Cash Out é uma novidade desta temporada (2018/19) — permite encerrar a aposta antes
do resultado e receber um valor parcial.
**Camada:** Bronze
**Fonte:** Cashouts.csv
**Atualização:** Ingestão única dos dados históricos da temporada

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| cashout_attempt_bet_id | TEXT | ID da aposta relacionada à tentativa | — |
| cashout_attempt_bet_cashout_id | TEXT | ID único da tentativa de cash out | — |
| cashout_attempt_bet_cashout_created | TEXT | Timestamp da tentativa (raw do CSV) | — |
| cashout_attempt_bet_cashout_status | TEXT | Resultado da tentativa | Verificar valores únicos após ingestão |
| cashout_attempt_cashout_amount | TEXT | Valor do cash out solicitado (raw) | Numérico como texto |
| ingested_at | TIMESTAMP | Momento da ingestão no banco | — |

## Notas

- Todos os campos são TEXT na Bronze. Tipos corretos são aplicados na Silver.
- Uma aposta pode ter múltiplas tentativas de cash out.
- O status deve ser analisado após ingestão para identificar os valores possíveis.
