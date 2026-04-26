# Stack e Convenções

## Stack

| Camada | Tecnologia | Versão | Observação |
|---|---|---|---|
| Linguagem | Python | 3.12+ | — |
| Dependências | uv | latest | Substitui pip/poetry |
| Banco de dados | PostgreSQL | 16 | Schemas: bronze, silver, gold |
| Infraestrutura | Docker + Compose | latest | Portabilidade total |
| Dashboard | Streamlit | >=1.32 | Interface analítica |
| Agente de IA | Agno | >=1.4 | Framework de agentes Python |
| LLM | Claude (Anthropic) | API | Via ANTHROPIC_API_KEY |
| Visualizações | Plotly | >=5.20 | Gráficos interativos no Streamlit |
| ORM/DB | SQLAlchemy | >=2.0 | Conexão Python-PostgreSQL |
| Driver DB | psycopg2-binary | >=2.9 | Adaptador PostgreSQL para Python |

## Convenções de Código

### Nomenclatura
- Arquivos Python: `snake_case.py`
- Funções e variáveis: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Arquivos SQL: `NNN_descricao.sql` (numerados para ordenação)
- Tabelas e colunas SQL: `snake_case`

### Comentários
**Todos os comentários devem ser escritos em português.**

### Branches
- `main` — código estável
- `feature/*` — novas funcionalidades
- `fix/*` — correções
- `docs/*` — documentação

### Commits
Seguir Conventional Commits:
- `feat:` — nova funcionalidade
- `fix:` — correção de bug
- `docs:` — documentação
- `chore:` — tarefas de manutenção
- `refactor:` — refatoração sem mudança de comportamento

## Variáveis de Ambiente

Ver `.env.example` para lista completa.
Nunca commitar o arquivo `.env`.
