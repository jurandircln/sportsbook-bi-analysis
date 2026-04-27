import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.db import get_engine
from src.dashboard.filters import filter_by_month_range, filter_by_values

st.set_page_config(
    page_title="Sportsbook BI — Futebol Romeno 2018/19",
    page_icon="⚽",
    layout="wide",
)

@st.cache_resource
def get_db_engine():
    return get_engine()


@st.cache_data(ttl=300)
def load_season_summary():
    engine = get_db_engine()
    return pd.read_sql(
        "SELECT * FROM gold.season_summary ORDER BY month",
        engine,
        parse_dates=["month"],
    )


@st.cache_data(ttl=300)
def load_customer_segments():
    engine = get_db_engine()
    return pd.read_sql(
        "SELECT segment, COUNT(*) AS customers FROM gold.customer_segments GROUP BY segment ORDER BY segment",
        engine,
    )


@st.cache_data(ttl=300)
def load_crm_performance():
    engine = get_db_engine()
    return pd.read_sql(
        """SELECT crm_level, customer_count, total_bets, total_turnover,
                  gross_revenue, avg_bets_per_customer, avg_gross_revenue_per_customer
           FROM gold.crm_performance
           ORDER BY gross_revenue DESC""",
        engine,
    )


@st.cache_data(ttl=300)
def load_cashout_analysis():
    engine = get_db_engine()
    return pd.read_sql(
        "SELECT * FROM gold.cashout_analysis ORDER BY month",
        engine,
        parse_dates=["month"],
    )


@st.cache_data(ttl=300)
def load_top_customers(n: int = 20):
    engine = get_db_engine()
    return pd.read_sql(
        f"""SELECT cp.customer_id, cp.gender, cp.age, cp.total_bets,
                   cp.total_turnover, cp.gross_revenue, cp.live_bets,
                   ROUND(cp.live_bets::NUMERIC / NULLIF(cp.total_bets, 0) * 100, 1) AS live_pct,
                   cs.segment, cs.crm_level, bp.preferred_channel
            FROM gold.customer_performance cp
            LEFT JOIN gold.customer_segments cs ON cs.customer_id = cp.customer_id
            LEFT JOIN gold.betting_preferences bp ON bp.customer_id = cp.customer_id
            WHERE cp.total_bets > 0
            ORDER BY cp.gross_revenue DESC
            LIMIT {n}""",
        engine,
    )


def fmt_brl(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ─── Header ───────────────────────────────────────────────────────────────────
st.title("Sportsbook BI — Futebol Romeno 2018/19")
st.caption("Temporada Set/2018 – Ago/2019 · dados atualizados em cache a cada 5 min")

# ─── KPIs ─────────────────────────────────────────────────────────────────────
summary = load_season_summary()
total_gr = summary["gross_revenue"].sum()
total_bets = summary["total_bets"].sum()
avg_live = summary["live_bet_pct"].mean()
total_customers_season = summary["total_customers"].max()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Gross Revenue (temporada)", fmt_brl(total_gr))
k2.metric("Total de Apostas", f"{int(total_bets):,}".replace(",", "."))
k3.metric("% Apostas Live (média)", f"{avg_live:.1f}%")
k4.metric("Clientes ativos (pico mensal)", f"{int(total_customers_season):,}".replace(",", "."))

st.divider()

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_season, tab_crm, tab_cashout, tab_customers, tab_agent = st.tabs(
    ["📅 Resumo da Temporada", "🏅 Performance CRM", "💰 Cashouts", "👥 Top Clientes", "🤖 Agente BI"]
)

# ── Tab 1: Resumo da Temporada ─────────────────────────────────────────────────
with tab_season:
    st.info(
        "Visão mensal da temporada Set/2018–Ago/2019: receita bruta, volume de apostas, "
        "evolução da base de clientes e participação de apostas ao vivo. "
        "Use o filtro de período para recortar os meses de interesse."
    )

    # Filtro de período
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


# ── Tab 2: Performance CRM ─────────────────────────────────────────────────────
with tab_crm:
    st.info(
        "Comparativo de performance entre os níveis do programa CRM: receita, apostas e valor médio por cliente. "
        "A distribuição de segmentos reflete o período completo da temporada — todos os clientes são classificados "
        "como \"novo\" porque o dataset disponível não contém histórico anterior a Set/2018. "
        "Use o filtro de nível CRM para isolar grupos específicos."
    )
    crm = load_crm_performance()
    segments = load_customer_segments()

    col_crm, col_seg = st.columns(2)

    with col_crm:
        fig_crm_gr = px.bar(
            crm,
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
    crm_display = crm.copy()
    crm_display["gross_revenue"] = crm_display["gross_revenue"].apply(fmt_brl)
    crm_display["total_turnover"] = crm_display["total_turnover"].apply(fmt_brl)
    crm_display["avg_gross_revenue_per_customer"] = crm_display["avg_gross_revenue_per_customer"].apply(fmt_brl)
    crm_display.columns = [
        "Nível CRM", "Clientes", "Apostas", "Turnover", "Gross Revenue",
        "Apostas/Cliente", "GR/Cliente"
    ]
    st.dataframe(crm_display, use_container_width=True, hide_index=True)


# ── Tab 3: Cashouts ────────────────────────────────────────────────────────────
with tab_cashout:
    st.info(
        "Análise mensal das tentativas de cash out: volume (sucesso vs. falha), "
        "taxa de sucesso e valor total resgatado. "
        "Use o filtro de período para focar em meses específicos."
    )
    cashouts = load_cashout_analysis()

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        fig_co_vol = px.bar(
            cashouts,
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
            cashouts,
            x="month",
            y="success_rate",
            title="Taxa de Sucesso de Cashout (%)",
            labels={"month": "Mês", "success_rate": "Taxa de Sucesso (%)"},
            markers=True,
        )
        fig_co_rate.update_layout(xaxis_tickformat="%b/%y", yaxis_range=[0, 100])
        st.plotly_chart(fig_co_rate, use_container_width=True)

    fig_co_amount = px.bar(
        cashouts,
        x="month",
        y="total_cashout_amount",
        title="Valor Total de Cashouts Realizados",
        labels={"month": "Mês", "total_cashout_amount": "Valor (R$)"},
        color_discrete_sequence=["#9467bd"],
    )
    fig_co_amount.update_layout(xaxis_tickformat="%b/%y")
    st.plotly_chart(fig_co_amount, use_container_width=True)


# ── Tab 4: Top Clientes ────────────────────────────────────────────────────────
with tab_customers:
    n_customers = st.slider("Número de clientes", min_value=10, max_value=100, value=20, step=10)
    top = load_top_customers(n_customers)

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


# ── Tab 5: Agente BI ───────────────────────────────────────────────────────────
with tab_agent:
    st.subheader("Agente BI — Pergunte em linguagem natural")
    st.caption(
        "Exemplos: *Qual mês teve maior gross revenue?* · "
        "*Como o nível Diamond se compara ao Bronze?* · "
        "*Qual canal tem maior % de apostas live?*"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "bi_agent" not in st.session_state:
        from src.agent.bi_agent import create_agent
        st.session_state.bi_agent = create_agent()

    # Exibe histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Faça uma pergunta sobre os dados da temporada..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando dados..."):
                try:
                    response = st.session_state.bi_agent.run(prompt)
                    answer = response.content if hasattr(response, "content") else str(response)
                except Exception as e:
                    answer = f"Erro ao consultar o agente: {e}"
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.messages:
        if st.button("Limpar conversa"):
            st.session_state.messages = []
            st.session_state.bi_agent = __import__(
                "src.agent.bi_agent", fromlist=["create_agent"]
            ).create_agent()
            st.rerun()
