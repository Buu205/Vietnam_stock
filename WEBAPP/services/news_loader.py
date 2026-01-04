from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import streamlit as st

from WEBAPP.core.constants import CACHE_TTL_WARM

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NEWS_DIR = PROJECT_ROOT / "DATA" / "processed" / "news"
NEWS_DATA_PATH = NEWS_DIR / "news_latest.parquet"
NEWS_SUMMARY_PATH = NEWS_DIR / "news_summary.json"
BSC_FORECAST_PATH = (
    PROJECT_ROOT / "DATA" / "processed" / "forecast" / "bsc" / "bsc_forecast_latest.csv"
)


@st.cache_data(ttl=CACHE_TTL_WARM, show_spinner=False)
def load_news_data(days: int = 3) -> pd.DataFrame:
    if not NEWS_DATA_PATH.exists():
        return pd.DataFrame()
    df = pd.read_parquet(NEWS_DATA_PATH)
    if "publish_time" in df.columns:
        publish_series = pd.to_datetime(df["publish_time"], errors="coerce", utc=True)
        df["publish_time"] = publish_series.dt.tz_convert(None)
        if days:
            now_utc = pd.Timestamp.utcnow()
            if now_utc.tzinfo is None:
                now_naive = now_utc
            else:
                now_naive = now_utc.tz_convert(None)
            cutoff = now_naive - pd.Timedelta(days=days)
            df = df[df["publish_time"] >= cutoff]
    return df.sort_values("publish_time", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_WARM, show_spinner=False)
def load_news_summary() -> dict:
    if NEWS_SUMMARY_PATH.exists():
        return json.loads(NEWS_SUMMARY_PATH.read_text())
    return {}


@st.cache_data(ttl=CACHE_TTL_WARM, show_spinner=False)
def load_bsc_symbols() -> set[str]:
    if not BSC_FORECAST_PATH.exists():
        return set()
    df = pd.read_csv(BSC_FORECAST_PATH)
    symbol_cols = [col for col in df.columns if "symbol" in col.lower()]
    if not symbol_cols:
        return set()
    symbols = (
        pd.concat([df[col] for col in symbol_cols], ignore_index=True)
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
    )
    return set(sym for sym in symbols if sym and sym.isalpha())


def compute_sentiment_overview(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {
            "count": 0,
            "avg_score": 0.0,
            "positive": 0,
            "neutral": 0,
            "negative": 0,
        }
    return {
        "count": int(len(df)),
        "avg_score": float(df["sentiment_score"].mean()),
        "positive": int((df["sentiment_label"] == "positive").sum()),
        "neutral": int((df["sentiment_label"] == "neutral").sum()),
        "negative": int((df["sentiment_label"] == "negative").sum()),
    }


def split_news_segments(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if df.empty:
        empty = df.iloc[0:0].copy()
        return empty, empty, empty
    market_df = df[df.get("news_category", "market") == "market"].copy()
    corporate_df = df[df.get("news_category", "market") == "corporate"].copy()
    bsc_df = corporate_df[corporate_df.get("is_bsc_symbol", False)].copy()
    other_df = corporate_df[~corporate_df.get("is_bsc_symbol", False)].copy()
    return market_df, bsc_df, other_df


def format_sentiment_label(label: str) -> str:
    mapping = {
        "positive": "🟢 Positive",
        "neutral": "⚪ Neutral",
        "negative": "🔴 Negative",
    }
    return mapping.get(label, label or "Neutral")

