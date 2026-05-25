# ⚡ 글로벌 에너지 마켓 대시보드

LPG / 석유화학 / 에너지 전환 시장의 핵심 지표를 실시간으로 추적하는 개인 학습 프로젝트입니다.
에너지 업계 취업 준비 과정에서 도메인 이해도를 높이기 위해 제작했습니다.

🔗 **[라이브 대시보드 보기](https://energy-dashboard-dlwldms7741.streamlit.app)**

---

## 📋 페이지 구성

### 📊 가격 현황 (Price Overview)
- **실시간 가격 스냅샷**: Brent·WTI 원유, USD/KRW·JPY·CNY 환율, 천연가스, 납사 Proxy
- **가격 추이 차트**: 3개월~2년 기간 선택 가능한 인터랙티브 차트
- **미국 프로판 현물가**: Mont Belvieu 기준 (EIA API 연동 시 실제 데이터)
- **PDH 마진 계산기**: 프로필렌 가격 직접 입력 → PDH 수익성 실시간 계산

### ⚗️ 석유화학 경제성 (Petrochemical Economics)
- **납사 vs 프로판 스프레드**: 석화 원료 경쟁력 방향성 추적 (Heating Oil을 납사 proxy로 활용)
- **공정별 비교표**: NCC(납사 크래커) · LCC(LPG 크래커) · PDH 원가 구조 비교
- **아시아 PDH 플랜트 지도**: 중국·한국·동남아·중동 주요 플랜트 입지 시각화
- **LPG 무역 흐름 다이어그램**: 수입 → 저장 → 내수/수출 흐름 정리

### 🌍 수요 & 에너지 전환 (Demand & Transition)
- **미국 LPG 수출량**: 셰일가스 혁명 이후 수출 증가 추이 (EIA 월별)
- **아시아 LPG 수요 구조**: 국가별·용도별(석화/가정/수송) 수요 비중
- **전기차(EV) 확산 추이**: 글로벌·한국 연간 판매량 및 누적 대수
- **신재생에너지 성장**: 태양광·풍력·전체 설비용량 누적 추이 (GW)

### 📰 뉴스 레이더 (News Radar)
- **실시간 RSS 수집**: Reuters · IEA · EIA · Argus Media · Oil Price.com
- **키워드 그룹 필터**: LPG·프로판 / 석유화학 / 원유·에너지 / 지정학 / 에너지전환 / LNG·가스 / 무역·운임
- **태그 자동 분류**: 기사별 관련 키워드 그룹 색상 태그 표시
- **북마크 기능**: 중요 기사 세션 내 저장

---

## 🧠 대시보드에서 추적하는 핵심 인사이트

| 지표 | 의미 |
|------|------|
| **유가(Brent/WTI)** | 납사 가격과 연동 → LPG 대체 수요 방향성 결정 |
| **납사-프로판 스프레드** | 양수일수록 LPG 원료 경쟁력 ↑ → PDH·LCC 가동률 증가 |
| **PDH 마진** | 프로필렌 - 프로판 원가 → LPG 수출 수요의 선행지표 |
| **미국 프로판 현물가** | 중동 CP 대안 → 아시아 수입 원가 하락 압력 |
| **USD/KRW** | 달러 결제 LPG 수입 원가에 직접 영향 |
| **EV 확산 속도** | 수송용 LPG 수요 감소 vs 석화용 PP 수요 증가 |

---

## 🔧 기술 스택

```
Python 3.9+
Streamlit       — 멀티페이지 웹 대시보드
Plotly          — 인터랙티브 차트 (area, line, bar, scatter_geo)
yfinance        — 실시간 유가·환율 (Yahoo Finance API)
feedparser      — RSS 뉴스 피드 수집
requests        — EIA API 호출
pandas          — 데이터 처리
```

---

## 📂 프로젝트 구조

```
energy_dashboard/
├── app.py                          # 메인 진입점 + 사이드바
├── requirements.txt
├── data/
│   └── fetchers.py                 # 모든 외부 API 호출 레이어
└── pages/
    ├── 01_Price_Overview.py
    ├── 02_Petrochemical_Economics.py
    ├── 03_Demand_and_Transition.py
    └── 04_News_Radar.py
```

---

## 🔑 EIA API 연동 (선택)

[eia.gov/opendata](https://www.eia.gov/opendata/register.php) 에서 무료 발급 후 사이드바에 입력하면 아래 실제 데이터가 활성화됩니다:
- 미국 Mont Belvieu 프로판 현물가 (주별)
- 미국 LPG 수출량 (월별)
- 미국 프로판 재고 (주별)

API 키 없이도 유가·환율·뉴스는 실시간으로 작동합니다.

---

## 💡 제작 배경

에너지 트레이딩·해외영업 직무 준비 과정에서 단순히 공부하는 것을 넘어,
글로벌 LPG 시장의 공급-수요-가격 메커니즘을 직접 데이터로 확인하고 싶어 제작했습니다.

- 중동 CP → 미국 Mont Belvieu Spot 가격 경쟁 구조
- PDH 마진이 LPG 수출 수요를 어떻게 결정하는지
- EV 확산과 신재생에너지 성장이 LPG 시장에 미치는 영향

이 세 가지 흐름을 한 화면에서 파악하는 것이 핵심 목표입니다.
