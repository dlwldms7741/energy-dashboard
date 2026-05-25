"""
Page 1 — Price Overview
실시간 유가·환율·미국 프로판 현물가 스냅샷 + 추이 차트
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.fetchers import (
    fetch_price_snapshot,
    fetch_price_history,
    fetch_us_propane_price,
    fetch_us_propane_stocks,
    calc_pdh_proxy_spread,
)

st.set_page_config(page_title="가격 현황", page_icon="📊", layout="wide")
st.title("📊 Price Overview")
st.caption("실시간 유가·환율·미국 프로판 현물가 — Yahoo Finance (15분 딜레이) + EIA API")

eia_key = st.session_state.get("eia_key")

# ── 1. Metric Cards ───────────────────────────────────────────────────────────
with st.spinner("시세 불러오는 중..."):
    snapshot = fetch_price_snapshot()

if snapshot:
    st.subheader("현재 주요 지표")
    keys_row1 = ["brent", "wti", "usdkrw", "usdjpy"]
    keys_row2 = ["natgas", "heating_oil", "usdcny"]

    def render_metric(key):
        d = snapshot.get(key)
        if not d:
            return
        delta_str = f"{d['change_pct']:+.2f}%"
        delta_color = "normal"
        st.metric(
            label=f"{d['name']}",
            value=f"{d['price']:,.4g} {d['unit']}",
            delta=delta_str,
            delta_color=delta_color,
        )

    cols1 = st.columns(4)
    for col, key in zip(cols1, keys_row1):
        with col:
            render_metric(key)

    cols2 = st.columns(4)
    for col, key in zip(cols2, keys_row2):
        with col:
            render_metric(key)

st.divider()

# ── 2. Price History Charts ────────────────────────────────────────────────────
st.subheader("가격 추이")

period_map = {"3개월": "3mo", "6개월": "6mo", "1년": "1y", "2년": "2y"}
sel_period = st.radio("기간", list(period_map.keys()), index=2, horizontal=True)
period = period_map[sel_period]

tab_crude, tab_fx, tab_propane = st.tabs(["원유 (Brent · WTI)", "환율 (USD/KRW)", "미국 프로판 현물가"])

with tab_crude:
    c1, c2 = st.columns(2)
    for col, key, color, name in [
        (c1, "brent", "#e63946", "Brent Crude (USD/bbl)"),
        (c2, "wti",   "#457b9d", "WTI Crude (USD/bbl)"),
    ]:
        with col:
            df = fetch_price_history(key, period)
            if not df.empty:
                fig = px.area(
                    df, x=df.index, y="Close",
                    title=name,
                    labels={"Close": "USD/bbl", "x": ""},
                    color_discrete_sequence=[color],
                )
                fig.update_layout(
                    margin=dict(l=0, r=0, t=40, b=0),
                    showlegend=False,
                    hovermode="x unified",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"{name} 데이터를 불러올 수 없습니다.")

    with st.expander("💡 원유 가격이 LPG 시장에 미치는 영향"):
        st.markdown(
            """
            - **유가 상승** → 납사(Naphtha) 가격 상승 → 석유화학사들이 LPG를 납사 대체 원료로 선호 → **LPG 수요 증가**
            - **유가 하락** → 납사 가격 하락 → LPG 경쟁력 상대적 약화 → 석화사 원료 선택 변화
            - 단, LPG는 별도의 Contract Price(CP) 체계로 거래되므로 유가와 완전히 연동되지는 않음
            - **중동 지정학 리스크** → 유가 급등 + LPG 공급 불안 동시 발생 가능
            """
        )

with tab_fx:
    df_fx = fetch_price_history("usdkrw", period)
    if not df_fx.empty:
        fig = px.line(
            df_fx, x=df_fx.index, y="Close",
            title="USD/KRW 환율 추이",
            labels={"Close": "KRW", "x": ""},
            color_discrete_sequence=["#2a9d8f"],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("환율 데이터를 불러올 수 없습니다.")

    with st.expander("💡 환율이 LPG 수입·수출에 미치는 영향"):
        st.markdown(
            """
            - LPG는 **달러(USD)로 결제** — 원화 약세(환율 상승) 시 수입 원가 상승, 국내 판매 마진 압박
            - 반대로 수출 수익은 달러 수취 → 원화 약세 시 원화 환산 수출 이익 증가
            - **일본·중국 바이어와의 협상**: 엔/위안 변동도 상대방의 구매력에 영향
            - 2022~2023 고환율·고물가 국면에서 E1 같은 LPG 수입사는 원가 압박을 크게 받음
            """
        )

with tab_propane:
    st.caption(
        "미국 Mont Belvieu 프로판 현물가 (USD/gallon) — EIA API | "
        + ("✅ EIA 키 연결됨" if eia_key else "⚠️ EIA 키 없음 — 샘플 데이터 표시 중")
    )
    df_prop = fetch_us_propane_price(eia_key)
    if not df_prop.empty:
        fig = px.line(
            df_prop, x="date", y="value",
            title="미국 프로판 현물가 (Mont Belvieu)",
            labels={"value": "USD/gallon", "date": ""},
            color_discrete_sequence=["#f4a261"],
        )
        fig.add_hline(
            y=df_prop["value"].mean(),
            line_dash="dash", line_color="gray",
            annotation_text=f"평균 ${df_prop['value'].mean():.3f}",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("EIA API 키를 사이드바에 입력하면 실제 데이터가 표시됩니다.")

    with st.expander("💡 미국 프로판 가격이 글로벌 LPG 시장에서 중요한 이유"):
        st.markdown(
            """
            - 미국은 **셰일가스 혁명** 이후 세계 최대 LPG 수출국으로 부상
            - Mont Belvieu(텍사스)는 미국 프로판 현물 거래의 기준 허브
            - 미국 프로판 가격 하락 → 아시아 수입 가격 하락 압력 → 동아시아 PDH 공장 원가 개선
            - 반대로 미국 한파(freeze-off) 등 재고 급감 이벤트 → 글로벌 프로판 가격 급등
            - **E1 관점**: 중동 CP가 높을 때 미국 Spot 구매·Swap 거래로 대안 확보 가능
            """
        )

st.divider()

# ── 3. PDH Margin Proxy ───────────────────────────────────────────────────────
st.subheader("PDH 마진 프록시 (프로필렌 고정 가정)")
st.caption(
    "PDH 마진 = 프로필렌 가격 - 프로판 원가. "
    "프로필렌은 유료 데이터라 아래에서 직접 입력 후 확인하세요."
)

propylene_price = st.number_input(
    "프로필렌 시장가 (USD/ton) — 직접 입력",
    min_value=300.0, max_value=2000.0, value=900.0, step=10.0,
    help="Platts/Argus 등에서 확인한 아시아 CFR 프로필렌 가격을 입력하세요."
)

df_prop2 = fetch_us_propane_price(eia_key)
df_spread = calc_pdh_proxy_spread(df_prop2, propylene_price)

if not df_spread.empty:
    df_spread["zone"] = df_spread["pdh_margin"].apply(
        lambda x: "수익 구간 (PDH 가동 유리)" if x > 0 else "손실 구간 (가동 축소 가능)"
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_spread["date"], y=df_spread["pdh_margin"],
        fill="tozeroy",
        line=dict(color="#2a9d8f", width=1.5),
        name="PDH 마진 (USD/ton)",
    ))
    fig.add_hline(y=0, line_color="red", line_dash="dash", annotation_text="손익분기")
    fig.update_layout(
        title=f"PDH 마진 프록시 (프로필렌 ${propylene_price:.0f}/ton 고정)",
        xaxis_title="", yaxis_title="USD/ton",
        hovermode="x unified",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    latest = df_spread["pdh_margin"].iloc[-1]
    if latest > 150:
        st.success(f"📈 현재 PDH 마진 ${latest:.0f}/ton — 가동 유인 강함 → 프로판 수요 증가 기대")
    elif latest > 0:
        st.info(f"📊 현재 PDH 마진 ${latest:.0f}/ton — 흑자 구간이나 마진 좁음")
    else:
        st.warning(f"📉 현재 PDH 마진 ${latest:.0f}/ton — 가동 축소 가능 → 프로판 수요 감소 우려")

    with st.expander("💡 PDH 마진을 왜 추적하는가"):
        st.markdown(
            """
            - **PDH 마진 > 0** → PDH 공장 수익성 있음 → 가동률 유지·확대 → 프로판 구매량 증가
            - **PDH 마진 축소/음수** → 공장 가동 줄임 → 프로판 수요 감소 → LPG 수출량 영향
            - 따라서 PDH 마진은 **LPG 수출 수요의 선행지표** 역할
            - 중국·동남아에 수십 개의 PDH 공장이 있으며, 이들이 E1의 핵심 수출 고객군
            - 프로필렌 실제 가격은 Platts/Argus 구독 필요 → 위 입력창에 직접 넣어서 확인
            """
        )
