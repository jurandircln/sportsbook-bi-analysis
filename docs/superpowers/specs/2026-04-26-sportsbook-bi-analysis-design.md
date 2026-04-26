# Design: Sportsbook BI Analysis — Estrutura Base do Projeto

**Data:** 2026-04-26  
**Status:** Aprovado  
**Repositório:** https://github.com/jurandircln/sportsbook-bi-analysis (público)

---

## 1. Contexto e Objetivo

Projeto de análise de dados da temporada de futebol romeno 2018/19 para o time de produto de Sportsbook. O objetivo é avaliar a performance da temporada e preparar recomendações para a próxima.

**Perguntas de negócio que o sistema deve responder:**
- Performance geral dos clientes (atividade de apostas, receita bruta)
- Comportamento da base: clientes novos, existentes e que saíram
- Preferências dos clientes: Live vs. Pre-event, Android vs. iOS, mercados preferidos, horários de aposta
- Performance por CRM level
- Destaques da temporada com sugestões para a próxima temporada

**Dados disponíveis (CSVs com dados mock):**
- `Cashouts.csv` — tentativas de cash out
- `Customer.csv` — base de clientes
- `Customer_crm_level.csv` — níveis CRM mensais por cliente
- `Events.csv` — informações de eventos esportivos
- `Sportsbook.csv` — atividade de apostas

---

## 2. Metodologia: Spec-Driven Development (SDD)

O projeto segue a metodologia SDD com 3 camadas de contexto hierárquicas:

- **Camada 1 — Negócio** (`docs/business-context/`): por que estamos construindo isso
- **Camada 2 — Produto** (`docs/product-context/`): o que estamos construindo e como funciona
- **Camada 3 — Engenharia** (`docs/technical-context/`): como estamos construindo, com que padrões

**Regra de código:** todo código deve ser comentado em português.

---

## 3. Estrutura do Repositório

```
sportsbook-bi-analysis/
├── .claude/
│   └── skills/
│       ├── db-modeling.md           ← guia de modelagem de banco
│       ├── create-adr.md            ← checklist e template para novos ADRs
│       ├── update-business-rules.md ← protocolo para atualizar regras de negócio da Silver
│       └── update-data-catalog.md   ← protocolo para revisar o catálogo de dados
├── .cursor/
│   ├── rules/                       ← regras globais da IA
│   ├── agents/                      ← agentes especializados
│   └── commands/                    ← comandos customizados
├── docs/
│   ├── business-context/
│   │   ├── vision.md
│   │   ├── personas.md
│   │   ├── journeys.md
│   │   ├── competitive.md
│   │   ├── kpis.md
│   │   └── features/
│   ├── product-context/
│   │   ├── features/
│   │   ├── business-rules.md
│   │   └── glossary.md
│   ├── technical-context/
│   │   ├── stack.md
│   │   ├── codebase-guide.md
│   │   ├── data-catalog/
│   │   │   ├── overview.md
│   │   │   ├── bronze/
│   │   │   │   ├── cashouts.md
│   │   │   │   ├── customer.md
│   │   │   │   ├── customer_crm_level.md
│   │   │   │   ├── events.md
│   │   │   │   └── sportsbook.md
│   │   │   ├── silver/
│   │   │   └── gold/
│   │   ├── api-specs/
│   │   └── adr/
│   │       ├── ADR-001-medallion-architecture.md
│   │       ├── ADR-002-database-modeling.md
│   │       ├── ADR-003-agno-agent-design.md
│   │       ├── ADR-004-stack-and-tooling.md
│   │       └── ADR-005-data-catalog.md
│   └── superpowers/
│       └── specs/
├── data/
│   └── raw/                         ← CSVs originais (não versionados via .gitignore)
├── src/
│   ├── ingestion/                   ← scripts de carga Bronze (CSV → PostgreSQL)
│   ├── transformation/              ← transformações Silver e Gold
│   ├── agent/                       ← agente Agno + SQL tools
│   └── dashboard/                   ← aplicação Streamlit
├── sql/
│   ├── bronze/                      ← DDLs da camada Bronze
│   ├── silver/                      ← DDLs e transformações Silver
│   └── gold/                        ← DDLs, views e métricas Gold
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pyproject.toml                   ← gerenciado por uv
└── CLAUDE.md
```

---

## 4. Stack e Ferramentas

| Camada | Tecnologia | Observação |
|---|---|---|
| Linguagem | Python 3.12+ | — |
| Gerenciador de dependências | uv | Substitui pip/poetry |
| Banco de dados | PostgreSQL 16 | Schemas: bronze, silver, gold |
| Infraestrutura | Docker + Docker Compose | Portabilidade total |
| Dashboard | Streamlit | Interface principal |
| Agente de IA | Agno (Python) | Framework de agentes |
| LLM | Claude (Anthropic) | Via API key em .env |
| IDE AI | Cursor + Claude Code | — |

---

## 5. Arquitetura Medalhão

### Bronze — dados brutos
- Ingestão direta dos CSVs sem transformação de negócio
- Preserva dados originais exatamente como chegaram
- Coluna `ingested_at` em todas as tabelas para rastreabilidade
- Schema PostgreSQL: `bronze`

### Silver — dados limpos e conformados
Regras de negócio críticas aplicadas nesta camada:
- **CRM Level forward-fill**: para meses entre dois registros, usa o nível mais recente atribuído
- **Gross Revenue**: `Turnover - Winnings`
- **Classificação de clientes**: novo / existente / saindo baseado na janela Set/2018–Ago/2019
- **Live vs. Pre-event**: comparação entre `Event_Start_Time` e `SportBetSettled_Placed`
- Tipagem correta de todas as colunas (datas, decimais, categorias)
- Schema PostgreSQL: `silver`

### Gold — métricas e visões analíticas
Tabelas e views prontas para consumo pelo Streamlit e pelo agente:

| Tabela/View | Conteúdo |
|---|---|
| `gold.customer_performance` | KPIs por cliente (turnover, gross revenue, total apostas) |
| `gold.customer_segments` | Classificação novo/existente/saindo + CRM level por período |
| `gold.betting_preferences` | Live vs. Pre-event, canal, mercado preferido, horário de aposta |
| `gold.crm_performance` | Performance agregada por CRM level |
| `gold.season_summary` | Visão consolidada da temporada 2018/19 |
| `gold.cashout_analysis` | Performance e adoção do recurso de cash out |

Schema PostgreSQL: `gold`

---

## 6. Agente Agno — Design Híbrido

### Abordagem
Híbrida: SQL tools pré-definidas para perguntas mapeadas + geração ad-hoc para perguntas fora do escopo.

### Tools pré-definidas

| Tool | Query alvo | Parâmetros |
|---|---|---|
| `get_customer_performance` | `gold.customer_performance` | `period`, `crm_level` |
| `get_customer_segments` | `gold.customer_segments` | `period` |
| `get_betting_preferences` | `gold.betting_preferences` | `segment`, `channel` |
| `get_crm_performance` | `gold.crm_performance` | `crm_level` |
| `get_season_summary` | `gold.season_summary` | — |
| `get_cashout_analysis` | `gold.cashout_analysis` | `period`, `status` |

### System prompt do agente
Inclui:
- Schema completo das tabelas Gold
- Definições do catálogo de dados
- Regras de negócio críticas (Gross Revenue, CRM forward-fill, classificação de clientes)
- Instruções de resposta em português

### Modo ad-hoc
Para perguntas fora do escopo das tools, o agente gera SQL com o schema como guardrail, executa e retorna resultado formatado.

---

## 7. Skills do Projeto

Localizadas em `.claude/skills/`:

| Skill | Quando invocar |
|---|---|
| `db-modeling.md` | Ao criar ou evoluir qualquer tabela/schema do banco |
| `create-adr.md` | Ao tomar qualquer decisão técnica relevante que tenha alternativas consideradas |
| `update-business-rules.md` | Ao alterar transformações da camada Silver ou adicionar novas regras |
| `update-data-catalog.md` | Ao adicionar/alterar tabelas, colunas ou métricas derivadas em qualquer camada |

---

## 8. ADRs Iniciais

Localizados em `docs/technical-context/adr/`:

| ADR | Decisão | Status |
|---|---|---|
| ADR-001 | Adoção da arquitetura medalhão com PostgreSQL | Aceita |
| ADR-002 | Modelagem inicial do banco — schema, tipos, granularidade por camada | Aceita |
| ADR-003 | Design do agente Agno — abordagem híbrida, Claude como LLM | Aceita |
| ADR-004 | Escolhas de stack — uv, Docker, Streamlit, Agno, PostgreSQL | Aceita |
| ADR-005 | Catálogo de dados como artefato de governança obrigatório | Aceita |

---

## 9. Catálogo de Dados

Localizado em `docs/technical-context/data-catalog/`.

Cada arquivo documenta:
- Definição da tabela e sua camada
- Colunas: nome, tipo, descrição, valores possíveis
- Regras de negócio aplicadas
- Fonte de origem
- Exemplos de valores quando relevante

**Protocolo de atualização:** qualquer alteração de schema ou nova métrica derivada exige atualização do catálogo na mesma PR/commit. Skill `update-data-catalog.md` deve ser invocada.

---

## 10. CLAUDE.md — Estrutura

O CLAUDE.md é o ponto de entrada obrigatório de toda sessão de desenvolvimento.

**Seções:**
1. Visão geral do projeto e problema de negócio
2. Metodologia SDD — referência às 3 camadas em `docs/`
3. Regras de código — comentários em português, convenções de nomenclatura
4. Arquitetura de dados — resumo do medalhão, referência ao catálogo
5. Skills disponíveis — tabela com skill, quando invocar, localização
6. ADRs ativos — lista com número, título e status
7. Governança — quando atualizar catálogo, criar ADR, atualizar regras de negócio
8. Stack — referência a `docs/technical-context/stack.md`
9. Como rodar o projeto — `docker compose up`, comandos uv, acesso ao Streamlit (porta 8501)

---

## 11. Docker Compose

Dois serviços:

```yaml
services:
  postgres:
    image: postgres:16
    # schemas bronze, silver, gold criados na inicialização
    # volume persistente para dados
    # dados raw/ montados para ingestão

  app:
    build: .
    # imagem Python 3.12 com uv
    # Streamlit na porta 8501
    # depende do postgres
```

Variáveis de ambiente (`.env.example`):
- `ANTHROPIC_API_KEY` — chave da API Claude
- `DATABASE_URL` — connection string PostgreSQL
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

---

## 12. GitHub

- **Repositório:** `https://github.com/jurandircln/sportsbook-bi-analysis`
- **Visibilidade:** público
- **Branch padrão:** `main`
- **Convenção de commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- **Primeira versão:** estrutura base do repositório (CLAUDE.md, docs/, skills, ADRs, docker-compose, pyproject.toml)
