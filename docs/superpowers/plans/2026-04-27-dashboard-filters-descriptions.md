# Dashboard — Filtros por Tab e Descrições de Painéis — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar filtros interativos por tab e descrições contextuais a cada painel do dashboard Streamlit, melhorando a capacidade de self-service analítico do usuário.

**Architecture:** Filtros pós-carregamento — os DataFrames são carregados integralmente do banco (já cacheados) e filtrados em Python via funções puras em `src/dashboard/filters.py`. Nenhuma query Gold ou Silver é alterada. A lógica de filtragem é isolada em módulo próprio para ser testável sem Streamlit.

**Tech Stack:** Python 3.12, Streamlit, Pandas, pytest

---

## Mapeamento de Arquivos

| Ação | Arquivo | Responsabilidade |
|------|---------|-----------------|
| Criar | `src/dashboard/filters.py` | Funções puras de filtragem de DataFrame |
| Criar | `tests/test_filters.py` | Testes unitários das funções de filtragem |
| Modificar | `src/dashboard/app.py` | UI: descrições, filtros, preload de clientes |

---

## Task 1: Criar módulo de filtros com testes

**Files:**
- Create: `src/dashboard/filters.py`
- Create: `tests/test_filters.py`

- [ ] **Step 1: Escrever os testes que vão falhar**

Criar o arquivo `tests/test_filters.py` com o conteúdo abaixo:

```python
import pandas as pd
from datetime import date
from src.dashboard.filters import filter_by_month_range, filter_by_values


def test_filter_by_month_range_retorna_linhas_no_intervalo():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2018-09-01", "2018-10-01", "2018-11-01"]),
        "value": [1, 2, 3],
    })
    result = filter_by_month_range(df, "month", date(2018, 9, 1), date(2018, 10, 1))
    assert list(result["value"]) == [1, 2]


def test_filter_by_month_range_retorna_vazio_quando_fora_do_intervalo():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2018-09-01"]),
        "value": [1],
    })
    result = filter_by_month_range(df, "month", date(2019, 1, 1), date(2019, 3, 1))
    assert len(result) == 0


def test_filter_by_month_range_retorna_tudo_quando_intervalo_completo():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2018-09-01", "2019-08-01"]),
        "value": [1, 2],
    })
    result = filter_by_month_range(df, "month", date(2018, 9, 1), date(2019, 8, 1))
    assert len(result) == 2


def test_filter_by_values_retorna_linhas_correspondentes():
    df = pd.DataFrame({"crm_level": ["Diamond", "Gold", "Silver"], "v": [1, 2, 3]})
    result = filter_by_values(df, "crm_level", ["Diamond", "Silver"])
    assert list(result["v"]) == [1, 3]


def test_filter_by_values_retorna_tudo_quando_lista_vazia():
    df = pd.DataFrame({"crm_level": ["Diamond", "Gold"], "v": [1, 2]})
    result = filter_by_values(df, "crm_level", [])
    assert len(result) == 2


def test_filter_by_values_retorna_vazio_quando_nenhum_corresponde():
    df = pd.DataFrame({"crm_level": ["Diamond", "Gold"], "v": [1, 2]})
    result = filter_by_values(df, "crm_level", ["Bronze"])
    assert len(result) == 0
```

- [ ] **Step 2: Executar os testes e confirmar que falham**

```bash
uv run pytest tests/test_filters.py -v
```

Esperado: `ImportError: cannot import name 'filter_by_month_range' from 'src.dashboard.filters'`

- [ ] **Step 3: Implementar o módulo de filtros**

Criar `src/dashboard/filters.py`:

```python
import pandas as pd
from datetime import date


def filter_by_month_range(
    df: pd.DataFrame, col: str, start: date, end: date
) -> pd.DataFrame:
    months = df[col].dt.date
    return df[(months >= start) & (months <= end)]


def filter_by_values(df: pd.DataFrame, col: str, values: list) -> pd.DataFrame:
    if not values:
        return df
    return df[df[col].isin(values)]
```

- [ ] **Step 4: Executar os testes e confirmar que passam**

```bash
uv run pytest tests/test_filters.py -v
```

Esperado: 6 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/dashboard/filters.py tests/test_filters.py
git commit -m "feat: adicionar módulo de filtros de DataFrame com testes"
```

---

## Task 2: Adicionar descrições nas tabs

**Files:**
- Modify: `src/dashboard/app.py`

- [ ] **Step 1: Adicionar import do módulo de filtros no topo de `app.py`**

Localizar a linha:
```python
from src.db import get_engine
```

Substituir por:
```python
from src.db import get_engine
from src.dashboard.filters import filter_by_month_range, filter_by_values
```

- [ ] **Step 2: Adicionar descrição na Tab 1 (Resumo da Temporada)**

Localizar em `app.py` (linha ~106):
```python
with tab_season:
    col_left, col_right = st.columns(2)
```

Substituir por:
```python
with tab_season:
    st.info(
        "Visão mensal da temporada Set/2018–Ago/2019: receita bruta, volume de apostas, "
        "evolução da base de clientes e participação de apostas ao vivo. "
        "Use o filtro de período para recortar os meses de interesse."
    )
    col_left, col_right = st.columns(2)
```

- [ ] **Step 3: Adicionar descrição na Tab 2 (Performance CRM)**

Localizar em `app.py` (linha ~160):
```python
with tab_crm:
    crm = load_crm_performance()
    segments = load_customer_segments()
```

Substituir por:
```python
with tab_crm:
    st.info(
        "Comparativo de performance entre os níveis do programa CRM: receita, apostas e valor médio por cliente. "
        "A distribuição de segmentos reflete o período completo da temporada — todos os clientes são classificados "
        "como \"novo\" porque o dataset disponível não contém histórico anterior a Set/2018. "
        "Use o filtro de nível CRM para isolar grupos específicos."
    )
    crm = load_crm_performance()
    segments = load_customer_segments()
```

- [ ] **Step 4: Adicionar descrição na Tab 3 (Cashouts)**

Localizar em `app.py` (linha ~199):
```python
with tab_cashout:
    cashouts = load_cashout_analysis()
```

Substituir por:
```python
with tab_cashout:
    st.info(
        "Análise mensal das tentativas de cash out: volume (sucesso vs. falha), "
        "taxa de sucesso e valor total resgatado. "
        "Use o filtro de período para focar em meses específicos."
    )
    cashouts = load_cashout_analysis()
```

- [ ] **Step 5: Verificar no browser que as 3 descrições aparecem corretamente**

> Nota: a Tab 4 (Top Clientes) recebe sua descrição na Task 6, que reconstrói o bloco inteiro.

```bash
docker compose up -d
```

Abrir http://localhost:8501 e confirmar o bloco azul de info no início das tabs 1, 2 e 3.

- [ ] **Step 6: Commit**

```bash
git add src/dashboard/app.py
git commit -m "feat: adicionar descrições contextuais no início das tabs do dashboard"
```

---

## Task 3: Filtro de período na Tab 1 (Resumo da Temporada)

**Files:**
- Modify: `src/dashboard/app.py`

- [ ] **Step 1: Substituir o conteúdo da Tab 1 para usar filtro de data**

Em `app.py`, dentro de `with tab_season:`, após o bloco `st.info(...)`, localizar:

```python
    col_left, col_right = st.columns(2)
```

Substituir todo o bloco `with tab_season:` a partir do `col_left` até o final da tab (antes de `# ── Tab 2`) pelo código abaixo:

```python
    min_date = summary["month"].min().date()
    max_date = summary["month"].max().date()
    date_range = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="season_date_range",
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        summary_f = filter_by_month_range(summary, "month", date_range[0], date_range[1])
    else:
        summary_f = summary

    col_left, col_right = st.columns(2)

    with col_left:
        fig_gr = px.bar(
            summary_f,
            x="month",
            y="gross_revenue",
            title="Gross Revenue Mensal",
            labels={"month": "Mês", "gross_revenue": "Gross Revenue (R$)"},
            color_discrete_sequence=["#1f77b4"],
        )
        fig_gr.update_layout(xaxis_tickformat="%b/%y")
        st.plotly_chart(fig_gr, use_container_width=True)

    with col_right:
        fig_bets = px.line(
            summary_f,
            x="month",
            y="total_bets",
            title="Volume de Apostas por Mês",
            labels={"month": "Mês", "total_bets": "Apostas"},
            markers=True,
        )
        fig_bets.update_layout(xaxis_tickformat="%b/%y")
        st.plotly_chart(fig_bets, use_container_width=True)

    fig_customers = px.area(
        summary_f,
        x="month",
        y=["total_customers", "new_customers"],
        title="Clientes Ativos e Novos por Mês",
        labels={"month": "Mês", "value": "Clientes", "variable": "Tipo"},
        color_discrete_map={
            "total_customers": "#2ca02c",
            "new_customers": "#ff7f0e",
        },
    )
    fig_customers.update_layout(xaxis_tickformat="%b/%y")
    st.plotly_chart(fig_customers, use_container_width=True)

    fig_live = px.line(
        summary_f,
        x="month",
        y="live_bet_pct",
        title="% Apostas Live por Mês",
        labels={"month": "Mês", "live_bet_pct": "% Live"},
        markers=True,
    )
    fig_live.update_layout(xaxis_tickformat="%b/%y", yaxis_range=[0, 100])
    st.plotly_chart(fig_live, use_container_width=True)
```

- [ ] **Step 2: Verificar no browser**

Abrir http://localhost:8501, ir para a Tab 1, selecionar um subperíodo (ex: Out/2018–Dez/2018) e confirmar que os 4 gráficos atualizam. Confirmar que os KPIs no topo da página **não mudam**.

- [ ] **Step 3: Commit**

```bash
git add src/dashboard/app.py
git commit -m "feat: adicionar filtro de período na tab Resumo da Temporada"
```

---

## Task 4: Filtro de período na Tab 3 (Cashouts)

**Files:**
- Modify: `src/dashboard/app.py`

- [ ] **Step 1: Substituir o conteúdo da Tab 3 para usar filtro de data**

Em `app.py`, dentro de `with tab_cashout:`, após o bloco `st.info(...)` e `cashouts = load_cashout_analysis()`, localizar:

```python
    col_c1, col_c2 = st.columns(2)
```

Inserir antes dessa linha:

```python
    min_date_co = cashouts["month"].min().date()
    max_date_co = cashouts["month"].max().date()
    date_range_co = st.date_input(
        "Período",
        value=(min_date_co, max_date_co),
        min_value=min_date_co,
        max_value=max_date_co,
        key="cashout_date_range",
    )
    if isinstance(date_range_co, tuple) and len(date_range_co) == 2:
        cashouts_f = filter_by_month_range(cashouts, "month", date_range_co[0], date_range_co[1])
    else:
        cashouts_f = cashouts

```

Em seguida, substituir todas as referências a `cashouts` nos gráficos abaixo por `cashouts_f`:

```python
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        fig_co_vol = px.bar(
            cashouts_f,
            x="month",
            y=["successful_attempts", "failed_attempts"],
            barmode="stack",
            title="Tentativas de Cashout por Mês",
            labels={"month": "Mês", "value": "Tentativas", "variable": "Status"},
            color_discrete_map={
                "successful_attempts": "#2ca02c",
                "failed_attempts": "#d62728",
            },
        )
        fig_co_vol.update_layout(xaxis_tickformat="%b/%y")
        st.plotly_chart(fig_co_vol, use_container_width=True)

    with col_c2:
        fig_co_rate = px.line(
            cashouts_f,
            x="month",
            y="success_rate",
            title="Taxa de Sucesso de Cashout (%)",
            labels={"month": "Mês", "success_rate": "Taxa de Sucesso (%)"},
            markers=True,
        )
        fig_co_rate.update_layout(xaxis_tickformat="%b/%y", yaxis_range=[0, 100])
        st.plotly_chart(fig_co_rate, use_container_width=True)

    fig_co_amount = px.bar(
        cashouts_f,
        x="month",
        y="total_cashout_amount",
        title="Valor Total de Cashouts Realizados",
        labels={"month": "Mês", "total_cashout_amount": "Valor (R$)"},
        color_discrete_sequence=["#9467bd"],
    )
    fig_co_amount.update_layout(xaxis_tickformat="%b/%y")
    st.plotly_chart(fig_co_amount, use_container_width=True)
```

- [ ] **Step 2: Verificar no browser**

Abrir http://localhost:8501, ir para a Tab 3, selecionar um subperíodo e confirmar que os 3 gráficos atualizam corretamente.

- [ ] **Step 3: Commit**

```bash
git add src/dashboard/app.py
git commit -m "feat: adicionar filtro de período na tab Cashouts"
```

---

## Task 5: Filtro de nível CRM na Tab 2 (Performance CRM)

**Files:**
- Modify: `src/dashboard/app.py`

- [ ] **Step 1: Adicionar filtro multiselect e aplicar na Tab 2**

Em `app.py`, dentro de `with tab_crm:`, após carregar os dados:

```python
    crm = load_crm_performance()
    segments = load_customer_segments()
```

Inserir logo após:

```python
    crm_levels = sorted(crm["crm_level"].dropna().unique().tolist())
    selected_crm = st.multiselect(
        "Nível CRM",
        options=crm_levels,
        default=crm_levels,
        key="crm_level_filter",
    )
    crm_f = filter_by_values(crm, "crm_level", selected_crm)

```

Em seguida, substituir as referências a `crm` nos gráficos e tabela por `crm_f`. A pizza de segmentos permanece usando `segments` sem filtro:

```python
    col_crm, col_seg = st.columns(2)

    with col_crm:
        fig_crm_gr = px.bar(
            crm_f,
            x="crm_level",
            y="gross_revenue",
            color="crm_level",
            title="Gross Revenue por Nível CRM",
            labels={"crm_level": "Nível CRM", "gross_revenue": "Gross Revenue (R$)"},
        )
        st.plotly_chart(fig_crm_gr, use_container_width=True)

    with col_seg:
        fig_seg = px.pie(
            segments,
            names="segment",
            values="customers",
            title="Distribuição de Segmentos de Clientes",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    st.subheader("Métricas por Nível CRM")
    crm_display = crm_f.copy()
    crm_display["gross_revenue"] = crm_display["gross_revenue"].apply(fmt_brl)
    crm_display["total_turnover"] = crm_display["total_turnover"].apply(fmt_brl)
    crm_display["avg_gross_revenue_per_customer"] = crm_display["avg_gross_revenue_per_customer"].apply(fmt_brl)
    crm_display.columns = [
        "Nível CRM", "Clientes", "Apostas", "Turnover", "Gross Revenue",
        "Apostas/Cliente", "GR/Cliente"
    ]
    st.dataframe(crm_display, use_container_width=True, hide_index=True)
```

- [ ] **Step 2: Verificar no browser**

Abrir http://localhost:8501, ir para a Tab 2, desmarcar alguns níveis no multiselect e confirmar que o gráfico de barras e a tabela atualizam. Confirmar que a pizza de segmentos **não muda**.

- [ ] **Step 3: Commit**

```bash
git add src/dashboard/app.py
git commit -m "feat: adicionar filtro de nível CRM na tab Performance CRM"
```

---

## Task 6: Filtros de segmento e gênero na Tab 4 (Top Clientes)

**Files:**
- Modify: `src/dashboard/app.py`

- [ ] **Step 1: Adicionar função de preload de clientes**

Em `app.py`, após a função `load_top_customers`, adicionar:

```python
@st.cache_data(ttl=300)
def load_customers_for_filter():
    engine = get_db_engine()
    return pd.read_sql(
        """SELECT cp.customer_id, cp.gender, cp.age, cp.total_bets,
                   cp.total_turnover, cp.gross_revenue, cp.live_bets,
                   ROUND(cp.live_bets::NUMERIC / NULLIF(cp.total_bets, 0) * 100, 1) AS live_pct,
                   cs.segment, cs.crm_level, bp.preferred_channel
            FROM gold.customer_performance cp
            LEFT JOIN gold.customer_segments cs ON cs.customer_id = cp.customer_id
            LEFT JOIN gold.betting_preferences bp ON bp.customer_id = cp.customer_id
            WHERE cp.total_bets > 0
            ORDER BY cp.gross_revenue DESC""",
        engine,
    )
```

- [ ] **Step 2: Substituir o conteúdo da Tab 4**

Localizar todo o bloco `with tab_customers:` e substituir por:

```python
with tab_customers:
    st.info(
        "Ranking dos clientes com maior receita bruta gerada na temporada. "
        "Combine os filtros de segmento e gênero com o seletor de quantidade "
        "para criar cortes customizados da base."
    )
    all_customers = load_customers_for_filter()

    segments_opts = sorted(all_customers["segment"].dropna().unique().tolist())
    genders_opts = sorted(all_customers["gender"].dropna().unique().tolist())

    col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
    with col_f1:
        selected_segments = st.multiselect(
            "Segmento",
            options=segments_opts,
            default=segments_opts,
            key="customer_segment_filter",
        )
    with col_f2:
        selected_genders = st.multiselect(
            "Gênero",
            options=genders_opts,
            default=genders_opts,
            key="customer_gender_filter",
        )
    with col_f3:
        n_customers = st.slider("Número de clientes", min_value=10, max_value=100, value=20, step=10)

    top = filter_by_values(all_customers, "segment", selected_segments)
    top = filter_by_values(top, "gender", selected_genders)
    top = top.head(n_customers)

    fig_top = px.bar(
        top,
        x="customer_id",
        y="gross_revenue",
        color="segment",
        hover_data=["total_bets", "live_pct", "crm_level", "preferred_channel"],
        title=f"Top {n_customers} Clientes por Gross Revenue",
        labels={
            "customer_id": "ID do Cliente",
            "gross_revenue": "Gross Revenue (R$)",
            "segment": "Segmento",
        },
        color_discrete_map={
            "novo": "#2ca02c",
            "existente": "#1f77b4",
            "saindo": "#d62728",
        },
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.subheader("Detalhes dos Top Clientes")
    top_display = top.copy()
    top_display["gross_revenue"] = top_display["gross_revenue"].apply(fmt_brl)
    top_display["total_turnover"] = top_display["total_turnover"].apply(fmt_brl)
    top_display.columns = [
        "ID", "Gênero", "Idade", "Apostas", "Turnover", "Gross Revenue",
        "Apostas Live", "% Live", "Segmento", "Nível CRM", "Canal Preferido"
    ]
    st.dataframe(top_display, use_container_width=True, hide_index=True)
```

- [ ] **Step 3: Verificar no browser**

Abrir http://localhost:8501, ir para a Tab 4 e confirmar:
- Filtros de segmento e gênero aparecem ao lado do slider
- Mudar o segmento atualiza o gráfico e a tabela
- O slider de quantidade opera sobre o resultado já filtrado (ex: filtrar só "existente" e pedir top 20 mostra os 20 melhores existentes)

- [ ] **Step 4: Executar suite de testes para garantir que nada quebrou**

```bash
uv run pytest tests/test_filters.py -v
```

Esperado: 6 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/dashboard/app.py
git commit -m "feat: adicionar filtros de segmento e gênero na tab Top Clientes"
```
