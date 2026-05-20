"""
Page 4 — News Radar
에너지 키워드 뉴스 실시간 수집 · 필터링 · 북마크
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.fetchers import fetch_news, ENERGY_KEYWORDS, NEWS_FEEDS

st.set_page_config(page_title="News Radar", page_icon="📰", layout="wide")
st.title("📰 News Radar")
st.caption("글로벌 에너지 뉴스 실시간 수집 — Reuters · IEA · EIA · Oil Price")

# ── Controls ─────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 1])

with col_ctrl1:
    selected_sources = st.multiselect(
        "뉴스 소스",
        options=list(NEWS_FEEDS.keys()),
        default=list(NEWS_FEEDS.keys()),
    )

with col_ctrl2:
    keyword_groups = {
        "LPG·프로판": ["LPG", "propane", "butane", "프로판"],
        "석유화학": ["PDH", "naphtha", "petrochemical", "propylene", "ethylene"],
        "원유·에너지": ["crude oil", "oil price", "OPEC", "energy"],
        "지정학": ["Middle East", "Saudi", "Iran", "OPEC"],
        "에너지 전환": ["energy transition", "renewable", "hydrogen", "EV", "electric vehicle"],
        "LNG·가스": ["LNG", "natural gas", "shale"],
        "무역·운임": ["VLGC", "shipping", "Vietnam", "Asia"],
    }
    selected_groups = st.multiselect(
        "키워드 그룹",
        options=list(keyword_groups.keys()),
        default=list(keyword_groups.keys()),
    )

with col_ctrl3:
    refresh = st.button("🔄 새로고침", use_container_width=True)

# Build active keywords from selected groups
active_keywords = []
for grp in selected_groups:
    active_keywords.extend(keyword_groups.get(grp, []))
active_keywords = list(set(active_keywords))

# ── Fetch ─────────────────────────────────────────────────────────────────────
with st.spinner("뉴스 피드 수집 중..."):
    all_news = fetch_news(max_per_feed=30)

# Filter by selected sources + active keywords
filtered = [
    n for n in all_news
    if n["source"] in selected_sources
    and any(kw.lower() in (n["title"] + n["summary"]).lower() for kw in active_keywords)
]

st.divider()

# ── Summary badges ────────────────────────────────────────────────────────────
badge_col = st.columns(5)
source_counts = {}
for n in filtered:
    source_counts[n["source"]] = source_counts.get(n["source"], 0) + 1

for i, (src, cnt) in enumerate(source_counts.items()):
    if i < 5:
        with badge_col[i]:
            st.metric(src, cnt, label_visibility="visible")

st.caption(f"총 {len(filtered)}개 기사 | 키워드: {', '.join(active_keywords[:8])}{'...' if len(active_keywords) > 8 else ''}")
st.divider()

# ── News cards ────────────────────────────────────────────────────────────────
if not filtered:
    st.info("조건에 맞는 뉴스가 없습니다. 키워드 그룹을 더 추가하거나 새로고침을 눌러주세요.")
else:
    # Bookmark state
    if "bookmarks" not in st.session_state:
        st.session_state["bookmarks"] = []

    for item in filtered[:40]:
        with st.container():
            c1, c2 = st.columns([10, 1])
            with c1:
                # Highlight matching keywords in title
                title_display = item["title"]
                st.markdown(f"#### [{title_display}]({item['link']})")

                # Tag badges
                matched_groups = [
                    grp for grp, kws in keyword_groups.items()
                    if any(kw.lower() in (item["title"] + item["summary"]).lower() for kw in kws)
                ]
                tag_colors = {
                    "LPG·프로판":    "#2a9d8f",
                    "석유화학":      "#457b9d",
                    "원유·에너지":   "#e63946",
                    "지정학":        "#6d6875",
                    "에너지 전환":   "#2d6a4f",
                    "LNG·가스":      "#f4a261",
                    "무역·운임":     "#e9c46a",
                }
                tags_html = " ".join(
                    f'<span style="background:{tag_colors.get(g,"#999")};color:white;'
                    f'padding:2px 8px;border-radius:12px;font-size:11px;">{g}</span>'
                    for g in matched_groups
                )
                st.markdown(tags_html, unsafe_allow_html=True)

                st.markdown(
                    f'<span style="color:#888;font-size:12px;">'
                    f'📡 {item["source"]}  &nbsp;|&nbsp;  🕐 {item["published"][:30] if item["published"] else "시간 미상"}'
                    f'</span>',
                    unsafe_allow_html=True,
                )
                if item["summary"]:
                    with st.expander("요약 보기"):
                        st.write(item["summary"])

            with c2:
                if st.button("🔖", key=f"bm_{item['link'][:40]}", help="북마크 저장"):
                    if item not in st.session_state["bookmarks"]:
                        st.session_state["bookmarks"].append(item)
                        st.toast(f"북마크 저장됨: {item['title'][:40]}...")

            st.divider()

# ── Bookmarks panel ───────────────────────────────────────────────────────────
if st.session_state.get("bookmarks"):
    st.subheader(f"🔖 저장된 북마크 ({len(st.session_state['bookmarks'])}개)")
    for bm in st.session_state["bookmarks"]:
        st.markdown(f"- [{bm['title']}]({bm['link']}) — {bm['source']}")
    if st.button("북마크 전체 삭제"):
        st.session_state["bookmarks"] = []
        st.rerun()
