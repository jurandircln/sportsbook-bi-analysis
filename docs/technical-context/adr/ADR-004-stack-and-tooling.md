# ADR-004: Stack e Ferramentas

**Data:** 2026-04-26
**Status:** Aceita

## Contexto

Precisávamos definir a stack completa do projeto garantindo: reprodutibilidade
do ambiente, velocidade de desenvolvimento, suporte a análise de dados e
integração com IA generativa.

## Decisão

- **Python 3.12** com **uv** para gerenciamento de dependências (mais rápido que pip/poetry)
- **PostgreSQL 16** como banco de dados (suporte completo a schemas, NUMERIC, índices)
- **Docker + Docker Compose** para portabilidade — qualquer dev sobe o ambiente com `docker compose up`
- **Streamlit** para o dashboard analítico (Python nativo, sem frontend separado)
- **Agno** como framework de agentes (Python nativo, suporte a tools e múltiplos LLMs)
- **Claude (Anthropic)** como LLM do agente (qualidade de raciocínio e SQL generation)
- **Plotly** para gráficos interativos dentro do Streamlit
- **SQLAlchemy 2.0** para conexão Python-PostgreSQL

## Consequências

Stack 100% Python reduz a curva de aprendizado. Docker garante que novos devs não
precisem configurar banco localmente. uv é significativamente mais rápido que pip
para instalar dependências. Aceita-se dependência de serviço externo (API Anthropic)
para funcionar o agente — sem a chave, o dashboard funciona mas o chat não.
