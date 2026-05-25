"""
Page 2 — Petrochemical Economics
납사 vs LPG 원료 경쟁 구조 · PDH 공정 이해 · 석화 수요 지도
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.fetchers import fetch_price_history, fetch_us_propane_price

st.set_page_config(page_title="석유화학 경제성", page_icon="⚗️", layout="wide")
st.title("⚗️ Petrochemical Economics")
st.caption("납사 vs 프로판 원료 경쟁 · PDH 마진 구조 · 아시아 석화 수요 지도")

eia_key = st.session_state.get("eia_key")

# ── 1. Naphtha vs Propane 경쟁 구조 설명 ─────────────────────────────────────
st.subheader("납사(Naphtha) vs 프로판(Propane) — 석화 원료 경쟁 구조")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown(
        """
        #### 왜 석화사는 원료를 바꾸는가?

        석유화학사의 목표는 **에틸렌·프로필렌을 최저 원가로 생산**하는 것입니다.
        두 원료 중 더 싼 쪽을 쓰거나, 전용 공정(PDH)으로 전환합니다.

        ```
        원료 선택 기준:
        납사 싸면 → NCC(납사 크래커) 가동률 ↑
        프로판 싸면 → LCC(LPG 크래커) or PDH 가동률 ↑
        ```

        **실무 포인트:**
        - 납사 대비 프로판이 $100/ton 이상 저렴하면 LPG 수요 급증
        - 미국 셰일가스 이후 프로판이 구조적으로 저렴해지는 국면 반복
        - 이것이 E1이 "납사 대체 LPG 공급에 지속 투자"하는 배경
        """
    )

with col_right:
    # 납사-프로판 가상 스프레드 차트 (heating oil as naphtha proxy)
    st.markdown("#### 납사 Proxy (Heating Oil) vs 프로판 스프레드")

    df_ho  = fetch_price_history("heating_oil", "1y")   # $/gallon
    df_prop = fetch_us_propane_price(eia_key)

    if not df_ho.empty and not df_prop.empty:
        # align on date
        ho = df_ho["Close"].resample("W").last().reset_index()
        ho.columns = ["date", "heating_oil_gal"]

        prop = df_prop.set_index("date")["value"].resample("W").last().reset_index()
        prop.columns = ["date", "propane_gal"]

        merged = pd.merge(ho, prop, on="date", how="inner")
        merged["spread"] = merged["heating_oil_gal"] - merged["propane_gal"]
        merged["color"]  = merged["spread"].apply(lambda x: "LPG 유리 (스프레드 양수)" if x > 0 else "납사 유리 (스프레드 음수)")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=merged["date"], y=merged["spread"],
            marker_color=merged["spread"].apply(lambda x: "#2a9d8f" if x > 0 else "#e76f51"),
            name="스프레드 (Heating Oil - Propane, $/gal)",
        ))
        fig.add_hline(y=0, line_color="black", line_dash="dash")
        fig.update_layout(
            title="납사 Proxy - 프로판 스프레드 (양수 = LPG 경쟁력 유리)",
            xaxis_title="", yaxis_title="USD/gallon",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "⚠️ Heating Oil은 납사의 근사치(proxy)입니다. "
            "실제 납사 가격은 Platts/Argus 구독 필요. "
            "스프레드 방향성 참고용으로 활용하세요."
        )
    else:
        st.info("가격 데이터 로딩 중 — EIA 키가 있으면 프로판 실제 데이터가 표시됩니다.")

st.divider()

# ── 2. 공정별 비교표 ──────────────────────────────────────────────────────────
st.subheader("공정별 비교 — NCC · LCC · PDH")

proc_df = pd.DataFrame({
    "공정": ["NCC (납사 크래커)", "LCC (LPG 크래커)", "PDH (프로판 탈수소화)"],
    "주원료": ["납사 (Naphtha)", "LPG (프로판+부탄)", "프로판 (순수)"],
    "주요 생산물": ["에틸렌★ + 프로필렌 + 부타디엔", "에틸렌 + 프로필렌★", "프로필렌★ (전용)"],
    "원가 결정 요인": ["유가 연동", "LPG CP/Spot", "프로판 Spot"],
    "경쟁력 유리 시점": ["유가 낮을 때", "프로판 < 납사 시", "프로판 저가 구조적 지속 시"],
    "아시아 주요 기업": ["LG화학·롯데케미칼", "일부 NCC 혼소", "중국·동남아 신규 플랜트"],
})
st.dataframe(proc_df, use_container_width=True, hide_index=True)

st.divider()

# ── 3. PDH 공장 지도 (아시아 주요 입지) ──────────────────────────────────────
st.subheader("아시아 PDH 플랜트 주요 입지 — E1의 잠재 수출 고객 지도")

pdh_plants = pd.DataFrame({
    "국가":     ["중국", "중국", "중국", "중국", "한국", "동남아(인도네시아)", "중동(사우디)"],
    "지역":     ["산둥성", "저장성", "광둥성", "허베이성", "여수", "자카르타 인근", "주베일"],
    "lat":      [36.6,   29.5,   23.1,   38.0,   34.7,   -6.2,   27.0],
    "lon":      [117.0,  120.0,  113.3,  114.5,  127.7,  107.0,  49.6],
    "규모":     ["대형", "대형", "중형", "중형", "중형", "대형", "대형"],
    "E1 관련도": ["핵심 수출 대상", "핵심 수출 대상", "수출 대상", "수출 대상",
                "국내 공급", "신규 시장", "수입 거래처 겸 경쟁"],
})

fig_map = px.scatter_geo(
    pdh_plants,
    lat="lat", lon="lon",
    hover_name="지역",
    hover_data={"국가": True, "규모": True, "E1 관련도": True, "lat": False, "lon": False},
    color="E1 관련도",
    size_max=15,
    projection="natural earth",
    title="아시아·중동 주요 PDH 플랜트 입지 (E1 수출 관련성 기준)",
    color_discrete_map={
        "핵심 수출 대상": "#e63946",
        "수출 대상":      "#457b9d",
        "국내 공급":      "#2a9d8f",
        "신규 시장":      "#f4a261",
        "수입 거래처 겸 경쟁": "#6d6875",
    },
)
fig_map.update_geos(
    showcoastlines=True, coastlinecolor="lightgray",
    showland=True, landcolor="#f8f9fa",
    showocean=True, oceancolor="#e8f4f8",
    showcountries=True, countrycolor="lightgray",
    lataxis_range=[-15, 55], lonaxis_range=[40, 145],
)
fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0), legend_title="E1 관련도")
st.plotly_chart(fig_map, use_container_width=True)
st.caption(
    "※ 위 입지 데이터는 공개 보고서 기반 시범 데이터입니다. "
    "실제 신규 플랜트는 뉴스 피드(📰 News Radar 페이지)에서 추적하세요."
)

st.divider()

# ── 4. 에너지 흐름 요약 다이어그램 (텍스트) ──────────────────────────────────
st.subheader("LPG 무역 흐름 — 수입에서 수출까지")

st.markdown(
    """
    ```
    ┌───────────────────────────────────────────────────────────┐
    │  공급 측 (Supply)                                          │
    │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  │
    │  │ 중동 산유국  │  │  미국 셰일  │  │ 기타 (싱가포르·  │  │
    │  │ (Saudi·UAE· │  │  (Mont      │  │  일본 등 Spot)   │  │
    │  │  Kuwait·    │  │   Belvieu)  │  │                  │  │
    │  │  Qatar)     │  │             │  │                  │  │
    │  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘  │
    │         └────────────────┼─────────────────┘            │
    │                          ↓ CP / Spot / Swap              │
    │                   ┌──────────────┐                       │
    │                   │  E1 수입·저장 │                       │
    │                   │ (여수·인천·  │                       │
    │                   │  대산 3기지)  │                       │
    │                   └──────┬───────┘                       │
    │              ┌───────────┼───────────┐                   │
    │              ↓           ↓           ↓                   │
    │       국내 내수판매   직수출 영업   중계무역(Trading)      │
    │       (42.6%)        (중국·일본· (중동→제3국)             │
    │                       베트남…)                            │
    │              ↓           ↓                               │
    │         운수·취사    PDH·NCC 공장                         │
    │           난방용    (석화 원료용)                         │
    └───────────────────────────────────────────────────────────┘
    ```
    """
)

with st.expander("📌 이 흐름에서 해외영업 담당자가 주목하는 포인트"):
    st.markdown(
        """
        | 포인트 | 내용 |
        |--------|------|
        | **수입 협상** | 중동 CP + 미국 Spot 중 어느 쪽이 유리한가? Swap 거래로 운임 절감 가능한가? |
        | **수출 영업** | 중국 PDH 공장의 가동률이 올라가는 시점에 프로판 공급 계약 체결 타이밍 |
        | **석화 B2B** | 납사 가격이 오를수록 LPG 대체 수요 증가 → 장기 SLA 계약 선점 기회 |
        | **리스크** | 중동 지정학 → CP 급등 + 공급 차질 동시 발생 시 대안 수입선 빠르게 전환 |
        """
    )
