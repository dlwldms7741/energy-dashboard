"""
Page 3 — Demand & Energy Transition
아시아 LPG 수요 추이 · EV 확산 속도 · 신재생에너지 성장
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.fetchers import fetch_us_lpg_exports

st.set_page_config(page_title="Demand & Transition", page_icon="🌍", layout="wide")
st.title("🌍 Demand & Energy Transition")
st.caption("아시아 LPG 수요 동향 · EV 확산 속도 · 신재생에너지 성장")

eia_key = st.session_state.get("eia_key")

# ── 1. 미국 LPG 수출량 ────────────────────────────────────────────────────────
st.subheader("미국 LPG 수출량 추이 (EIA 월별 데이터)")
st.caption("미국의 LPG 수출 증가는 글로벌 공급 확대의 핵심 신호입니다.")

df_exp = fetch_us_lpg_exports(eia_key)

if not df_exp.empty:
    fig = px.bar(
        df_exp.tail(24), x="date", y="value",
        title="미국 LPG 수출량 (천 배럴/일, 최근 24개월)",
        labels={"value": "천 배럴/일", "date": ""},
        color_discrete_sequence=["#457b9d"],
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    # Static illustrative chart
    st.info("EIA API 키를 입력하면 실제 미국 LPG 수출 데이터를 표시합니다. 아래는 개요 데이터입니다.")
    static_data = pd.DataFrame({
        "연도": [2010, 2012, 2014, 2016, 2018, 2020, 2022, 2023],
        "수출량_천배럴일": [80, 150, 320, 580, 830, 1050, 1380, 1450],
        "비고": ["셰일 초기", "셰일 성장", "셰일 확대", "아시아 수요↑",
                "미·중 무역전쟁", "코로나 수요↓", "역대최대", "지속 성장"],
    })
    fig = px.bar(
        static_data, x="연도", y="수출량_천배럴일",
        title="미국 LPG 수출량 증가 추이 (천 배럴/일, 개요)",
        labels={"수출량_천배럴일": "천 배럴/일"},
        color_discrete_sequence=["#457b9d"],
        text="비고",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

with st.expander("💡 미국 LPG 수출 증가가 아시아 시장에 미치는 영향"):
    st.markdown(
        """
        - 2010년대 셰일가스 혁명 → 미국이 세계 최대 LPG 수출국으로 급부상
        - 아시아(한국·일본·중국·인도)로의 VLGC(초대형 LPG 운반선) 수송 급증
        - 공급 다변화: 중동 CP 의존도 낮추고 미국 Spot 가격 활용 가능해짐
        - **E1 관점**: 미국 셰일 LPG 도입선 활용으로 수입 원가 경쟁력 확보
        """
    )

st.divider()

# ── 2. 아시아 LPG 수요 구조 (정적 데이터) ────────────────────────────────────
st.subheader("아시아 LPG 수요 구조 — 국가별·용도별")

col1, col2 = st.columns(2)

with col1:
    country_demand = pd.DataFrame({
        "국가": ["중국", "인도", "일본", "한국", "동남아(기타)", "중동"],
        "LPG수요_백만톤": [47, 29, 15, 8, 12, 18],
        "성장률_연간": ["+5%", "+6%", "-1%", "-2%", "+8%", "+3%"],
        "주요용도": ["석화·가정용", "가정·LPG차량", "산업·가정", "석화·수송", "가정용급증", "산업·수출"],
    })
    fig1 = px.pie(
        country_demand, values="LPG수요_백만톤", names="국가",
        title="아시아 주요국 LPG 수요 비중 (참고용 개요)",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig1.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("⚠️ 참고용 개요 데이터 — 최신 수치는 IEA Energy Statistics 확인")

with col2:
    use_demand = pd.DataFrame({
        "용도": ["석유화학 원료 (PDH·LCC)", "가정용 (취사·난방)", "수송용 (LPG차량)", "산업·기타"],
        "비중": [38, 32, 18, 12],
        "트렌드": ["성장↑", "안정→", "감소↓", "안정→"],
    })
    fig2 = px.bar(
        use_demand, x="용도", y="비중",
        title="아시아 LPG 용도별 수요 비중 (%)",
        color="트렌드",
        color_discrete_map={"성장↑": "#2a9d8f", "안정→": "#457b9d", "감소↓": "#e76f51"},
        labels={"비중": "%"},
    )
    fig2.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_tickangle=-20,
        showlegend=True,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("⚠️ 참고용 개요 데이터 — IEA/BP Statistical Review 기준")

st.divider()

# ── 3. EV 확산 vs LPG 수송 수요 ──────────────────────────────────────────────
st.subheader("전기차(EV) 확산 속도 — LPG 수송 수요 위협 요인")

ev_data = pd.DataFrame({
    "연도":     [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "글로벌EV판매_만대": [202, 221, 312, 675, 1020, 1400, 1700],
    "글로벌EV누적_만대": [510, 730, 1040, 1720, 2740, 4140, 5840],
    "한국EV판매_만대":   [3.1, 3.4, 4.6, 10.1, 16.2, 18.9, 20.0],
})

tab_global, tab_korea = st.tabs(["글로벌 EV 판매", "한국 EV 판매"])

with tab_global:
    fig_ev = go.Figure()
    fig_ev.add_trace(go.Bar(
        x=ev_data["연도"], y=ev_data["글로벌EV판매_만대"],
        name="연간 판매량 (만대)", marker_color="#2a9d8f",
        yaxis="y",
    ))
    fig_ev.add_trace(go.Scatter(
        x=ev_data["연도"], y=ev_data["글로벌EV누적_만대"],
        name="누적 대수 (만대)", line=dict(color="#e63946", width=2),
        yaxis="y2", mode="lines+markers",
    ))
    fig_ev.update_layout(
        title="글로벌 전기차 판매·누적 추이",
        yaxis=dict(title="연간 판매 (만대)"),
        yaxis2=dict(title="누적 (만대)", overlaying="y", side="right"),
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_ev, use_container_width=True)
    st.caption("⚠️ 참고용 개요 데이터 — IEA Global EV Outlook 기반")

with tab_korea:
    fig_kr = px.bar(
        ev_data, x="연도", y="한국EV판매_만대",
        title="한국 전기차 연간 판매량 (만대)",
        labels={"한국EV판매_만대": "만대"},
        color_discrete_sequence=["#457b9d"],
    )
    fig_kr.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_kr, use_container_width=True)
    st.caption("⚠️ 참고용 개요 데이터 — 한국자동차협회 기반")

with st.expander("💡 EV 확산이 LPG 시장에 의미하는 것"):
    st.markdown(
        """
        | 영향 방향 | 내용 |
        |----------|------|
        | **수송용 LPG 수요 감소** | LPG 택시·버스 → 전기차 전환 가속. 한국은 이미 감소 추세 |
        | **석화 LPG 수요 성장** | EV 배터리·플라스틱 부품 → PP(폴리프로필렌) 수요 증가 → PDH 원료 프로판 수요 ↑ |
        | **E1 전략적 대응** | 수송용 충전소 → EV 복합충전소(Orange Plus)로 전환 중 |
        | **장기 시나리오** | 수송 수요 감소 < 석화 수요 성장 → 총 LPG 수요는 당분간 유지 전망 |
        """
    )

st.divider()

# ── 4. 글로벌 신재생에너지 성장 ──────────────────────────────────────────────
st.subheader("글로벌 신재생에너지 성장 — 에너지 전환 속도")

re_data = pd.DataFrame({
    "연도":     [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    "태양광_GW": [505,  627,  714,  843, 1053, 1419, 1870],
    "풍력_GW":   [591,  623,  733,  824,  899,  1017, 1130],
    "총재생_GW": [2351, 2537, 2799, 3064, 3372, 3870, 4450],
})

fig_re = go.Figure()
fig_re.add_trace(go.Scatter(
    x=re_data["연도"], y=re_data["태양광_GW"],
    name="태양광 (GW)", line=dict(color="#f4a261", width=2),
    fill="tonexty" if False else None,
))
fig_re.add_trace(go.Scatter(
    x=re_data["연도"], y=re_data["풍력_GW"],
    name="풍력 (GW)", line=dict(color="#2a9d8f", width=2),
))
fig_re.add_trace(go.Scatter(
    x=re_data["연도"], y=re_data["총재생_GW"],
    name="전체 신재생 (GW)", line=dict(color="#457b9d", width=2, dash="dot"),
))
fig_re.update_layout(
    title="글로벌 신재생에너지 설비용량 누적 (GW)",
    xaxis_title="", yaxis_title="GW",
    hovermode="x unified",
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(orientation="h", y=-0.15),
)
st.plotly_chart(fig_re, use_container_width=True)
st.caption("⚠️ 참고용 개요 데이터 — IEA Renewables Report 기반")

col_a, col_b = st.columns(2)
with col_a:
    with st.expander("💡 신재생 성장이 LPG/에너지 시장에 미치는 영향"):
        st.markdown(
            """
            - 신재생 급성장 → 장기적으로 화석연료 수요 감소 압력
            - 단, 신재생 **간헐성(날씨 의존)** → LNG·LPG 백업 수요는 유지
            - E1이 LNG 발전사업 진입한 이유: 신재생 확대 시 필요한 '피크 보완' 역할
            - **에너지 전환의 속도**: 생각보다 빠르지 않음 → LPG의 10~20년 역할은 지속
            """
        )
with col_b:
    with st.expander("💡 수소경제와 LPG 인프라의 시너지"):
        st.markdown(
            """
            - LPG와 수소는 저장·운반·안전관리 측면에서 물성 유사
            - LPG 저장기지 → 수소 저장·유통 인프라로 전환 가능성
            - E1의 캐나다 청정수소 100억 투자 (2023) 는 이 시나리오의 첫 단계
            - 수소 사회 = LPG 인프라 보유 기업의 또 다른 성장 기회
            """
        )
