# Catálogo: bronze.customer_crm_level

**Descrição:** Histórico de níveis CRM mensais por cliente. Registros existem apenas
nos meses em que houve mudança de nível — meses sem registro devem receber o último
nível atribuído via forward-fill (aplicado na Silver).
**Camada:** Bronze
**Fonte:** Customer_crm_level.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| customer_id | TEXT | ID do cliente | Numérico como texto |
| date_yearmonth | TEXT | Mês de atribuição do nível (raw) | Formato a verificar após ingestão |
| crm_level | TEXT | Nível CRM atribuído | Verificar valores únicos após ingestão |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Regras de Negócio

- **RN-003 (forward-fill):** Registros existem apenas nos meses de mudança. Para meses
  intermediários, usar o nível mais recente. Aplicado na Silver.
- Exemplo: Bronze em Out/18 e Silver em Jan/19 → Nov/18 e Dez/18 são Bronze.

## Notas

- Não existe um registro para cada mês de cada cliente — isso é intencional.
- A tabela `silver.customer_crm_level` terá um registro por mês por cliente após o forward-fill.
