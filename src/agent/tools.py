"""
Tools pré-definidas do agente BI.
Cada tool executa uma query parametrizável na camada Gold e retorna JSON.
"""
import json
from typing import Optional
import pandas as pd
from agno.tools import Toolkit
from src.db import get_engine

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def _to_json(df: pd.DataFrame) -> str:
    return df.to_json(orient="records", date_format="iso", force_ascii=False)


class SportsbookTools(Toolkit):
    def __init__(self):
        super().__init__(name="sportsbook_tools")
        self.register(self.get_season_summary)
        self.register(self.get_crm_performance)
        self.register(self.get_customer_segments)
        self.register(self.get_customer_performance)
        self.register(self.get_betting_preferences)
        self.register(self.get_cashout_analysis)

    def get_season_summary(self) -> str:
        """Retorna o resumo mensal da temporada: total de apostas, gross revenue,
        clientes ativos, novos clientes e % apostas live para cada mês de Set/2018 a Ago/2019."""
        df = pd.read_sql(
            "SELECT month, total_customers, new_customers, total_bets, "
            "total_turnover, total_winnings, gross_revenue, live_bet_pct "
            "FROM gold.season_summary ORDER BY month",
            _get_engine(),
        )
        return _to_json(df)

    def get_crm_performance(self) -> str:
        """Retorna métricas agregadas por nível CRM (Bronze, Silver, Gold, Platinum, Diamond):
        número de clientes, total de apostas, turnover, gross revenue e médias por cliente."""
        df = pd.read_sql(
            "SELECT crm_level, customer_count, total_bets, total_turnover, "
            "total_winnings, gross_revenue, avg_bets_per_customer, "
            "avg_turnover_per_customer, avg_gross_revenue_per_customer "
            "FROM gold.crm_performance ORDER BY gross_revenue DESC",
            _get_engine(),
        )
        return _to_json(df)

    def get_customer_segments(self) -> str:
        """Retorna a distribuição de clientes por segmento (novo, existente, saindo)
        com datas da primeira e última aposta e nível CRM mais recente."""
        df = pd.read_sql(
            "SELECT segment, COUNT(*) AS customer_count, "
            "MIN(first_bet_date) AS earliest_first_bet, "
            "MAX(last_bet_date) AS latest_last_bet "
            "FROM gold.customer_segments GROUP BY segment ORDER BY segment",
            _get_engine(),
        )
        return _to_json(df)

    def get_customer_performance(
        self,
        limit: int = 20,
        segment: Optional[str] = None,
        min_bets: Optional[int] = None,
    ) -> str:
        """Retorna performance dos clientes ordenada por gross revenue decrescente.
        Parâmetros opcionais: limit (padrão 20), segment ('novo'/'existente'/'saindo'),
        min_bets (mínimo de apostas para filtrar)."""
        conditions = ["cp.total_bets > 0"]
        if segment:
            conditions.append(f"cs.segment = '{segment}'")
        if min_bets:
            conditions.append(f"cp.total_bets >= {int(min_bets)}")
        where = "WHERE " + " AND ".join(conditions)

        df = pd.read_sql(
            f"""SELECT cp.customer_id, cp.gender, cp.age, cp.total_bets,
                       cp.total_turnover, cp.total_winnings, cp.gross_revenue,
                       cp.live_bets, cp.pre_event_bets,
                       cp.cashout_attempts, cp.successful_cashouts,
                       cs.segment, cs.crm_level
                FROM gold.customer_performance cp
                LEFT JOIN gold.customer_segments cs ON cs.customer_id = cp.customer_id
                {where}
                ORDER BY cp.gross_revenue DESC
                LIMIT {int(limit)}""",
            _get_engine(),
        )
        return _to_json(df)

    def get_betting_preferences(
        self,
        limit: int = 20,
        channel: Optional[str] = None,
    ) -> str:
        """Retorna preferências de apostas dos clientes: canal preferido, mercado preferido,
        tipo de aposta preferido, % apostas live e hora de pico.
        Parâmetro opcional: channel para filtrar por canal ('Android', 'iOS', 'Web', etc.)."""
        conditions = []
        if channel:
            conditions.append(f"bp.preferred_channel = '{channel}'")
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        df = pd.read_sql(
            f"""SELECT bp.customer_id, bp.preferred_channel, bp.preferred_market,
                       bp.preferred_bet_type, bp.live_bet_pct, bp.peak_hour,
                       cs.segment, cs.crm_level
                FROM gold.betting_preferences bp
                LEFT JOIN gold.customer_segments cs ON cs.customer_id = bp.customer_id
                {where}
                ORDER BY bp.live_bet_pct DESC
                LIMIT {int(limit)}""",
            _get_engine(),
        )
        return _to_json(df)

    def get_cashout_analysis(self) -> str:
        """Retorna análise mensal de cashouts: total de tentativas, sucessos, falhas,
        taxa de sucesso (%), valor total e valor médio dos cashouts realizados."""
        df = pd.read_sql(
            "SELECT month, total_attempts, successful_attempts, failed_attempts, "
            "success_rate, total_cashout_amount, avg_cashout_amount "
            "FROM gold.cashout_analysis ORDER BY month",
            _get_engine(),
        )
        return _to_json(df)
