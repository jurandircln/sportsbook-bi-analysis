# Guia do Codebase

## Estrutura de Diretórios

```
src/
├── ingestion/        ← scripts de carga Bronze: lê CSVs e insere em bronze.*
├── transformation/   ← transformações Silver e Gold: aplica regras de negócio
├── agent/            ← agente Agno com tools SQL e integração Claude
└── dashboard/        ← aplicação Streamlit com abas de análise e chat

sql/
├── bronze/           ← DDLs das tabelas bronze.* (referência de schema)
├── silver/           ← DDLs das tabelas silver.*
└── gold/             ← DDLs das tabelas gold.*

docker/
└── init.sql          ← script executado na inicialização do PostgreSQL
```

## Padrão Arquitetural

O projeto segue separação por responsabilidade de dados:

1. **Ingestion** lê os CSVs de `data/raw/` e insere na Bronze sem transformação.
   Cada arquivo CSV tem um script de ingestão correspondente.

2. **Transformation** lê da Bronze, aplica regras de negócio e escreve na Silver.
   Em seguida, agrega da Silver para a Gold. Cada camada tem módulo separado.

3. **Agent** expõe tools SQL que consultam a Gold. Integra com Claude via Agno.
   O system prompt inclui schema da Gold e regras de negócio do catálogo.

4. **Dashboard** consome a Gold diretamente via SQLAlchemy para visualizações,
   e chama o agente para respostas conversacionais.

## Fluxo de Dados

```
data/raw/*.csv
    ↓ (ingestion/)
bronze.* (dados brutos)
    ↓ (transformation/silver/)
silver.* (dados limpos + regras de negócio)
    ↓ (transformation/gold/)
gold.* (métricas analíticas)
    ↓               ↓
dashboard/        agent/
(Streamlit)    (Agno + Claude)
```

## Conexão com o Banco

Usar `DATABASE_URL` do `.env` via SQLAlchemy:

```python
# Exemplo de conexão (será implementado em src/ingestion/)
from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))
```
