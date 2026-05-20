"""
Global Energy Market Dashboard
================================
A personal project to understand LPG / petrochemical / energy-transition
market dynamics — built as domain preparation for a career in energy trading.

Run:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Global Energy Market Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar — EIA API key (optional) ─────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Energy Dashboard")
    st.caption("Global LPG · Petrochemical · Energy Transition")
    st.divider()

    eia_key = st.text_input(
        "EIA API Key (optional)",
        type="password",
        placeholder="무료 등록: eia.gov/opendata",
        help="없으면 유가·환율·뉴스만 실시간 표시됩니다. "
             "EIA 키가 있으면 미국 프로판 가격·재고·수출 데이터를 불러옵니다.",
    )
    st.divider()
    st.markdown(
        """
        **데이터 소스**
        - 유가·환율: Yahoo Finance (15분 딜레이)
        - 프로판·재고·수출: EIA API (주별/월별)
        - 뉴스: Reuters · IEA · EIA · Oil Price RSS
        """
    )
    st.caption("Made as a domain-learning project — 2026")

# Store EIA key in session state so pages can access it
st.session_state["eia_key"] = eia_key or None

# ── Landing page ──────────────────────────────────────────────────────────────
st.title("Global Energy Market Dashboard")
st.markdown(
    "LPG / 석유화학 / 에너지 전환 시장의 핵심 지표를 한 화면에서 추적합니다. "
    "왼쪽 사이드바의 페이지를 선택하세요."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info("**📊 Price Overview**\n\nBrent·WTI·프로판·환율\n실시간 스냅샷")
with col2:
    st.info("**⚗️ Petrochemical Economics**\n\n납사 vs 프로판 스프레드\nPDH 마진 지표")
with col3:
    st.info("**🌍 Demand & Transition**\n\n아시아 LPG 수요\nEV·신재생 전환 속도")
with col4:
    st.info("**📰 News Radar**\n\n에너지 키워드 뉴스\n실시간 피드 + 필터")
