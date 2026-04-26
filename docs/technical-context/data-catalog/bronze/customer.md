# Catálogo: bronze.customer

**Descrição:** Base de clientes da plataforma de Sportsbook.
**Camada:** Bronze
**Fonte:** Customer.csv
**Atualização:** Ingestão única dos dados históricos

## Colunas

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| customer_id | TEXT | ID único do cliente | Numérico como texto |
| customer_datecreation_id | TEXT | Data de cadastro do cliente na plataforma (raw) | — |
| customer_gender_name | TEXT | Gênero do cliente | Verificar após ingestão |
| customer_birthday | TEXT | Data de nascimento (raw) | — |
| ingested_at | TIMESTAMP | Momento da ingestão | — |

## Notas

- `customer_id` é numérico mas armazenado como TEXT na Bronze.
- Data de nascimento pode conter valores nulos ou inconsistentes — tratar na Silver.
