"""
Data fetching layer — all external API calls live here.
Each function returns a dict or DataFrame; callers decide how to display.
"""

import datetime
import requests
import feedparser
import pandas as pd
import yfinance as yf

# ── Yahoo Finance ─────────────────────────────────────────────────────────────

YAHOO_TICKERS = {
    "brent":   "BZ=F",
    "wti":     "CL=F",
    "usdkrw":  "USDKRW=X",
    "usdjpy":  "USDJPY=X",
    "usdcny":  "USDCNY=X",
    "natgas":  "NG=F",
    "heating_oil": "HO=F",   # naphtha proxy (closest liquid market)
}

def fetch_price_snapshot() -> dict:
    """
    Returns current price + 1-day change for key commodities and FX.
    {ticker_key: {"price": float, "change_pct": float, "name": str, "unit": str}}
    """
    results = {}
    label_map = {
        "brent":       ("Brent Crude",      "USD/bbl"),
        "wti":         ("WTI Crude",         "USD/bbl"),
        "usdkrw":      ("USD/KRW",           "KRW"),
        "usdjpy":      ("USD/JPY",           "JPY"),
        "usdcny":      ("USD/CNY",           "CNY"),
        "natgas":      ("Henry Hub Natural Gas", "USD/MMBtu"),
        "heating_oil": ("Heating Oil (납사 Proxy)", "USD/gal"),
    }
    for key, symbol in YAHOO_TICKERS.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="2d", interval="1d")
            if len(hist) >= 2:
                prev  = hist["Close"].iloc[-2]
                curr  = hist["Close"].iloc[-1]
                chg   = (curr - prev) / prev * 100
            elif len(hist) == 1:
                curr  = hist["Close"].iloc[-1]
                chg   = 0.0
            else:
                continue
            name, unit = label_map.get(key, (key, ""))
            results[key] = {"price": round(float(curr), 4),
                            "change_pct": round(float(chg), 2),
                            "name": name, "unit": unit}
        except Exception:
            pass
    return results


def fetch_price_history(key: str, period: str = "1y") -> pd.DataFrame:
    """Returns OHLCV DataFrame for a given ticker key."""
    symbol = YAHOO_TICKERS.get(key)
    if not symbol:
        return pd.DataFrame()
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=True)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()


# ── EIA API (U.S. Energy Information Administration) ─────────────────────────
# Register free at https://www.eia.gov/opendata/

EIA_BASE = "https://api.eia.gov/v2"

def fetch_eia_series(series_id: str, api_key: str, limit: int = 52) -> pd.DataFrame:
    """Generic EIA v2 fetcher. Returns DataFrame with columns [date, value]."""
    try:
        url = f"{EIA_BASE}/seriesid/{series_id}"
        params = {"api_key": api_key, "length": limit}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get("response", {}).get("data", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df = df.rename(columns={"period": "date", "value": "value"})
        df["date"]  = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.sort_values("date").dropna()
    except Exception:
        return pd.DataFrame()


# EIA series IDs (no API key needed for demo — swap None with your key)
EIA_SERIES = {
    # U.S. propane spot price (Mont Belvieu, Texas) — $/gallon, weekly
    "us_propane_spot": "PET.EER_EPLLPA_PF4_Y35NY_DPG.W",
    # U.S. LPG exports (thousand barrels/day), monthly
    "us_lpg_exports":  "PET.MLLEXUS1.M",
    # U.S. propane stocks (thousand barrels), weekly
    "us_propane_stocks": "PET.WPRSTUS1.W",
}


def fetch_us_propane_price(api_key=None) -> pd.DataFrame:
    if not api_key:
        return _mock_propane_series()
    return fetch_eia_series(EIA_SERIES["us_propane_spot"], api_key, limit=104)


def fetch_us_lpg_exports(api_key=None) -> pd.DataFrame:
    if not api_key:
        return pd.DataFrame()
    return fetch_eia_series(EIA_SERIES["us_lpg_exports"], api_key, limit=24)


def fetch_us_propane_stocks(api_key=None) -> pd.DataFrame:
    if not api_key:
        return pd.DataFrame()
    return fetch_eia_series(EIA_SERIES["us_propane_stocks"], api_key, limit=104)


def _mock_propane_series() -> pd.DataFrame:
    """Placeholder when EIA key is absent — shows shape of data."""
    import numpy as np
    dates = pd.date_range(end=datetime.date.today(), periods=104, freq="W")
    vals  = 0.65 + 0.15 * np.sin(range(104)) + np.random.normal(0, 0.03, 104)
    return pd.DataFrame({"date": dates, "value": vals.clip(0.4, 1.2)})


# ── RSS News Feeds ────────────────────────────────────────────────────────────

NEWS_FEEDS = {
    "Reuters Energy":    "https://feeds.reuters.com/reuters/businessNews",
    "IEA News":          "https://www.iea.org/news/rss",
    "Argus Media":       "https://www.argusmedia.com/rss/latest-news",
    "EIA Today":         "https://www.eia.gov/rss/news.xml",
    "Oil Price.com":     "https://oilprice.com/rss/main",
}

ENERGY_KEYWORDS = [
    "LPG", "propane", "butane", "naphtha", "PDH", "LNG",
    "crude oil", "oil price", "OPEC", "energy transition",
    "petrochemical", "refinery", "Middle East", "Saudi", "VLGC",
    "shale", "hydrogen", "EV", "electric vehicle", "renewable",
    "Vietnam", "Asia gas", "프로판", "에너지",
]


def fetch_news(max_per_feed: int = 20) -> list[dict]:
    """
    Fetches and merges RSS items from all feeds.
    Filters by ENERGY_KEYWORDS.
    Returns list of dicts: {title, summary, link, published, source}
    """
    items = []
    for source, url in NEWS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title   = getattr(entry, "title",   "")
                summary = getattr(entry, "summary", "")
                text    = (title + " " + summary).lower()
                if any(kw.lower() in text for kw in ENERGY_KEYWORDS):
                    items.append({
                        "title":     title,
                        "summary":   summary[:300],
                        "link":      getattr(entry, "link", "#"),
                        "published": getattr(entry, "published", ""),
                        "source":    source,
                    })
        except Exception:
            pass
    # sort newest first (best-effort)
    items.sort(key=lambda x: x["published"], reverse=True)
    return items


# ── Derived / Calculated metrics ─────────────────────────────────────────────

def calc_pdh_proxy_spread(propane_df: pd.DataFrame,
                          propylene_usd_per_ton: float = 900.0) -> pd.DataFrame:
    """
    PDH margin proxy = propylene price ($/ton) - propane feedstock cost ($/ton).
    Propane $/gallon → $/ton: 1 ton propane ≈ 476 gallons (density ~0.51 t/m³).
    We use a fixed propylene price since it's behind paywalls;
    annotate clearly as illustrative.
    """
    if propane_df.empty:
        return pd.DataFrame()
    df = propane_df.copy()
    df["propane_usd_ton"] = df["value"] * 476   # $/gal → $/ton approximation
    df["pdh_margin"]      = propylene_usd_per_ton - df["propane_usd_ton"]
    return df
