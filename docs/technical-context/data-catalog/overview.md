# Catálogo de Dados — Visão Geral

O catálogo de dados é a fonte de verdade sobre o significado de cada campo,
tabela e métrica do projeto. Ele previne que pessoas diferentes interpretem
os mesmos dados de formas distintas.

## Como usar

Antes de implementar qualquer análise, query ou feature do agente, consulte
o catálogo para entender o que cada campo representa e quais regras foram aplicadas.

## Organização

O catálogo segue a mesma estrutura da arquitetura medalhão:

| Camada | Localização | Conteúdo |
|---|---|---|
| Bronze | `bronze/` | Dados brutos dos CSVs, tipos TEXT |
| Silver | `silver/` | Dados transformados com regras de negócio |
| Gold | `gold/` | Métricas analíticas para consumo |

## Protocolo de Atualização

Qualquer alteração de schema ou nova métrica → invocar skill `update-data-catalog`.
O catálogo é commitado junto com o DDL ou código na mesma PR/commit.

## Fontes de Dados

Todos os dados são da temporada de futebol romeno 2018/19 (Set/2018 – Ago/2019).

| Arquivo CSV | Tabela Bronze | Descrição |
|---|---|---|
| Cashouts.csv | bronze.cashouts | Tentativas de cash out |
| Customer.csv | bronze.customer | Base de clientes |
| Customer_crm_level.csv | bronze.customer_crm_level | Níveis CRM mensais |
| Events.csv | bronze.events | Eventos esportivos |
| Sportsbook.csv | bronze.sportsbook | Atividade de apostas |
