# Catálogo: bronze.events

**Descrição:** Informações sobre os eventos esportivos disponíveis para apostas na temporada.
**Camada:** Bronze
**Fonte:** Events.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| event_id | TEXT | ID único do evento | Numérico como texto |
| event_sport_name | TEXT | Tipo de esporte | Verificar após ingestão (foco: Football) |
| event_class_name | TEXT | Classe do evento | Verificar após ingestão |
| event_type_name | TEXT | Tipo de liga | Verificar após ingestão (foco: Romanian Football) |
| event_name | TEXT | Nome do evento (ex: Time A vs Time B) | — |
| event_start_time | TEXT | Horário real de início do evento (raw) | — |
| event_end_time | TEXT | Horário real de término do evento (raw) | — |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Notas

- `event_start_time` é crítico para a regra RN-002 (Live vs. Pre-event).
- O dataset pode conter eventos de outros esportes além do futebol romeno.
  Filtrar por `event_sport_name` e `event_type_name` quando necessário.
