# Catálogo: bronze.sportsbook

**Descrição:** Registro de todas as apostas realizadas e liquidadas na temporada.
Esta é a tabela principal de atividade — fonte para os KPIs de Turnover, Winnings
e Gross Revenue.
**Camada:** Bronze
**Fonte:** Sportsbook.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| sportbetsettled_bet_id | TEXT | ID único da aposta | — |
| bettype_name | TEXT | Tipo de aposta | Verificar após ingestão |
| market_template_name | TEXT | Mercado da aposta (ex: Match Winner, Both Teams to Score) | Verificar após ingestão |
| sportbetsettled_customer_id | TEXT | ID do cliente que fez a aposta | Referência a bronze.customer |
| sportbetsettled_settled | TEXT | Timestamp de liquidação da aposta (raw) | — |
| sportbetsettled_placed | TEXT | Timestamp de colocação da aposta (raw) | — |
| channel_name | TEXT | Dispositivo/canal usado | Verificar após ingestão (Android, iOS, Web) |
| sportbetsettled_event_id | TEXT | ID do evento apostado | Referência a bronze.events |
| turnover | TEXT | Valor apostado em moeda local (raw) | Numérico como texto |
| winnings | TEXT | Ganhos do cliente em moeda local (raw) | Numérico como texto |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Regras de Negócio

- **RN-001 (Gross Revenue):** Calculado na Silver como `turnover - winnings`
- **RN-002 (Live vs. Pre-event):** `is_live = (placed_at >= event_start_time)`
  requer JOIN com `silver.events` para obter `event_start_time`

## Notas

- `turnover` e `winnings` são armazenados como TEXT na Bronze — converter para
  NUMERIC(12,2) na Silver.
- Uma aposta com `winnings = 0` significa que o cliente perdeu a aposta.
- `gross_revenue` positivo = casa ganhou; negativo = casa pagou mais do que recebeu.
