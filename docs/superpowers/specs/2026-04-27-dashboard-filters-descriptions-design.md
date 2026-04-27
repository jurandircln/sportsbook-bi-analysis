# Design: Filtros por Tab e Descrições de Painéis

**Data:** 2026-04-27
**Escopo:** `src/dashboard/app.py`

## Contexto

O dashboard Streamlit do Sportsbook BI apresenta análises da temporada de futebol romeno 2018/19.
Três melhorias foram identificadas para aumentar a capacidade de self-service do usuário:

1. Filtros por tab para recortes customizados da análise
2. Investigação e documentação do dado de segmentos (100% "novo")
3. Descrições contextuais no início de cada tab

### Achado da análise exploratória — Segmentos

O `Sportsbook.csv` contém registros apenas de 2018-09-01 a 2019-08-31 (zero registros pré-temporada).
A classificação 100% "novo" está **correta** — a lógica Gold está certa; é limitação do dataset.
Essa informação deve ser documentada na descrição da tab de Performance CRM.

## Abordagem Escolhida

**Filtros pós-carregamento (Abordagem A):** filtros aplicados sobre DataFrames já carregados em Python,
sem alteração nas queries SQL ou na camada Gold. Justificativa: datasets pequenos (≤12 linhas mensais),
custo de implementação baixo, sem impacto no cache ou nas queries existentes.

## Design

### 1. Filtros por Tab

#### Tab 1 — Resumo da Temporada
- Componente: `st.date_input("Período", value=(min_date, max_date), min_value, max_value)`
- Default: range completo da temporada (Set/2018–Ago/2019)
- Escopo: filtra os 4 gráficos (Gross Revenue, Volume de Apostas, Clientes, % Live)
- **Não afeta:** KPIs globais no topo da página (representam a temporada inteira)

#### Tab 2 — Performance CRM
- Componente: `st.multiselect("Nível CRM", options=crm_levels, default=todos)`
- Escopo: filtra as barras de Gross Revenue por CRM e a tabela de métricas
- **Não afeta:** pizza de segmentos (representa o universo de clientes, independente de CRM)

#### Tab 3 — Cashouts
- Componente: `st.date_input("Período", ...)` — mesmo padrão da Tab 1
- Escopo: filtra os 3 gráficos (tentativas, taxa de sucesso, valor total)

#### Tab 4 — Top Clientes
- Componentes adicionados ao lado do slider existente:
  - `st.multiselect("Segmento", options=["novo", "existente", "saindo"], default=todos)`
  - `st.multiselect("Gênero", options=genders, default=todos)`
- Escopo: filtros aplicados sobre o DataFrame; slider de quantidade opera sobre o resultado filtrado

#### Tab 5 — Agente BI
- Sem filtros (não aplicável)

### 2. Descrições das Tabs

Componente: `st.info(...)` posicionado logo abaixo do título de cada tab.

| Tab | Texto |
|-----|-------|
| Resumo da Temporada | Visão mensal da temporada Set/2018–Ago/2019: receita bruta, volume de apostas, evolução da base de clientes e participação de apostas ao vivo. Use o filtro de período para recortar os meses de interesse. |
| Performance CRM | Comparativo de performance entre os níveis do programa CRM: receita, apostas e valor médio por cliente. A distribuição de segmentos reflete o período completo da temporada — todos os clientes são classificados como "novo" porque o dataset disponível não contém histórico anterior a Set/2018. Use o filtro de nível CRM para isolar grupos específicos. |
| Cashouts | Análise mensal das tentativas de cash out: volume (sucesso vs. falha), taxa de sucesso e valor total resgatado. Use o filtro de período para focar em meses específicos. |
| Top Clientes | Ranking dos clientes com maior receita bruta gerada na temporada. Combine os filtros de segmento e gênero com o seletor de quantidade para criar cortes customizados da base. |
| Agente BI | Sem alteração — descrição já existente é adequada. |

## Arquivos Afetados

- `src/dashboard/app.py` — único arquivo a modificar

## Fora de Escopo

- Alterações nas queries Gold ou Silver
- Filtros globais (sidebar)
- Persistência de filtros entre tabs via session state
- KPIs globais filtráveis
