# CLAUDE.md — Sportsbook BI Analysis

Leia este arquivo no início de toda sessão de desenvolvimento.
Ele é o contrato de trabalho do projeto.

## Visão Geral

Análise de dados da temporada de futebol romeno 2018/19 para o time de produto de Sportsbook.
O objetivo é avaliar a performance da temporada e preparar recomendações para a próxima.

**Repositório:** https://github.com/jurandircln/sportsbook-bi-analysis
**Temporada analisada:** Setembro 2018 – Agosto 2019

**Dados disponíveis (CSVs em `data/raw/`):**
- `Cashouts.csv` — tentativas de cash out
- `Customer.csv` — base de clientes
- `Customer_crm_level.csv` — níveis CRM mensais
- `Events.csv` — eventos esportivos
- `Sportsbook.csv` — atividade de apostas

## Regras de Código

- **Todos os comentários devem ser escritos em português**
- Nomes de arquivos: `snake_case`
- Funções e variáveis: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Classes: `PascalCase`
- Commits: Conventional Commits — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`

## Metodologia SDD — 3 Camadas de Contexto

O projeto segue Spec-Driven Development. Consulte as camadas antes de implementar:

| Camada | Localização | Pergunta respondida |
|---|---|---|
| Negócio | `docs/business-context/` | Por que estamos construindo isso? |
| Produto | `docs/product-context/` | O que estamos construindo? |
| Engenharia | `docs/technical-context/` | Como estamos construindo? |

## Arquitetura de Dados

Arquitetura **Medalhão** com 3 schemas no PostgreSQL:

| Camada | Schema | Propósito |
|---|---|---|
| Bronze | `bronze` | Dados brutos dos CSVs, tipos TEXT, sem transformação |
| Silver | `silver` | Dados tipados com regras de negócio aplicadas |
| Gold | `gold` | Métricas analíticas prontas para consumo |

**Regras críticas da camada Silver:**
- `gross_revenue = turnover - winnings`
- `is_live = placed_at >= event_start_time`
- CRM Level: forward-fill para meses sem registro
- Segmentos: novo / existente / saindo (ver ADR-002)

**Catálogo de dados:** `docs/technical-context/data-catalog/`

## Skills Disponíveis

| Skill | Quando invocar | Arquivo |
|---|---|---|
| `db-modeling` | Ao criar ou alterar qualquer tabela/schema | `.claude/skills/db-modeling.md` |
| `create-adr` | Ao tomar decisão técnica relevante com alternativas | `.claude/skills/create-adr.md` |
| `update-business-rules` | Ao alterar transformações da Silver | `.claude/skills/update-business-rules.md` |
| `update-data-catalog` | Ao adicionar/alterar tabelas, colunas ou métricas | `.claude/skills/update-data-catalog.md` |

## ADRs Ativos

| ADR | Título | Status |
|---|---|---|
| ADR-001 | Arquitetura Medalhão com PostgreSQL | Aceita |
| ADR-002 | Modelagem Inicial do Banco de Dados | Aceita |
| ADR-003 | Design do Agente Agno — Abordagem Híbrida | Aceita |
| ADR-004 | Stack e Ferramentas | Aceita |
| ADR-005 | Catálogo de Dados como Artefato de Governança | Aceita |

Localização: `docs/technical-context/adr/`

## Governança

### Quando criar um ADR
- Ao adotar nova tecnologia ou biblioteca
- Ao definir padrão arquitetural
- Ao rejeitar abordagem que parecia óbvia
- Ao fazer mudança que quebra padrão anterior
→ Invocar skill `create-adr`

### Quando atualizar o catálogo de dados
- Ao adicionar tabela, coluna ou schema novos
- Ao criar métricas derivadas na Gold
- Ao alterar tipos de dados
→ Invocar skill `update-data-catalog`

### Quando atualizar business-rules.md
- Ao alterar transformação da Silver
- Ao identificar nova regra de negócio
→ Invocar skill `update-business-rules`

## Stack

Ver detalhes em `docs/technical-context/stack.md`.

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12+ |
| Dependências | uv |
| Banco | PostgreSQL 16 |
| Infraestrutura | Docker + Docker Compose |
| Dashboard | Streamlit |
| Agente de BI | Agno (Python) |
| LLM | Claude via Anthropic API |

## Como Rodar o Projeto

```bash
# 1. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com sua ANTHROPIC_API_KEY

# 2. Subir todos os serviços
docker compose up -d

# 3. Verificar containers
docker compose ps

# 4. Acessar o dashboard
# http://localhost:8501

# 5. Conectar ao banco (desenvolvimento)
docker compose exec postgres psql -U sportsbook -d sportsbook_db
```

**Comandos úteis:**
```bash
docker compose logs -f          # ver logs em tempo real
docker compose down             # parar serviços
docker compose down -v          # parar e remover volumes (reset do banco)
uv sync                         # instalar/atualizar dependências Python
uv run pytest                   # executar testes
```
