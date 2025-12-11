"""Utilities to fetch, enrich, and persist news data via vnstock_news."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Set

import pandas as pd

from . import PROJECT_ROOT, PROCESSED_NEWS_DIR, RAW_NEWS_DIR

logger = logging.getLogger("news_pipeline")

try:
    from vnstock_news.core.crawler import Crawler
    from vnstock_news.core.batch import BatchCrawler
except ImportError as exc:  # pragma: no cover - handled at runtime
    Crawler = None  # type: ignore
    BatchCrawler = None  # type: ignore
    logger.error("vnstock_news is required: %s", exc)


DEFAULT_SITES = [
    "cafef",
    "cafebiz",
    "vnexpress",
    "vietstock",
    "plo",
    "ktsg",
]

ECONOMIC_SOURCES = {
    "cafef",
    "cafebiz",
    "vnexpress",
    "vietstock",
    "ktsg",
    "dddn",
}

POSITIVE_KEYWORDS = [
    "tăng trưởng",
    "lạc quan",
    "kỷ lục",
    "vượt",
    "bứt phá",
    "tích cực",
    "lợi nhuận",
    "khởi sắc",
    "hồi phục",
    "mở rộng",
    "kế hoạch",
    "thành công",
]

NEGATIVE_KEYWORDS = [
    "giảm",
    "suy giảm",
    "áp lực",
    "lỗ",
    "thua lỗ",
    "thấp nhất",
    "khó khăn",
    "đi xuống",
    "đình trệ",
    "cảnh báo",
    "tụt dốc",
    "khủng hoảng",
    "scandal",
]

BSC_FORECAST_PATH = (
    PROJECT_ROOT / "calculated_results" / "forecast" / "bsc" / "bsc_forecast_latest.csv"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect and process market news.")
    parser.add_argument(
        "--sites",
        nargs="+",
        default=DEFAULT_SITES,
        help="List of vnstock_news site keys to crawl.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max number of articles per site.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.4,
        help="Delay between article detail requests (seconds).",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=3,
        help="Only keep articles within the last N days.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_NEWS_DIR,
        help="Directory to store raw snapshots.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROCESSED_NEWS_DIR,
        help="Directory to store processed datasets.",
    )
    return parser.parse_args()


def ensure_dependencies() -> None:
    if Crawler is None or BatchCrawler is None:  # pragma: no cover - runtime guard
        logger.error(
            "vnstock_news is not installed. Install it before running the pipeline."
        )
        sys.exit(1)


def load_bsc_symbols() -> Set[str]:
    if not BSC_FORECAST_PATH.exists():
        logger.warning("BSC forecast file not found at %s", BSC_FORECAST_PATH)
        return set()

    df = pd.read_csv(BSC_FORECAST_PATH)
    symbol_cols = [col for col in df.columns if "symbol" in col.lower()]
    if not symbol_cols:
        return set()
    symbols: Set[str] = set()
    for col in symbol_cols:
        symbols.update(
            df[col]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(".", "", regex=False)
            .tolist()
        )
    return {sym for sym in symbols if sym.isalpha() and 2 < len(sym) <= 5}


def compute_sentiment(text: str) -> tuple[float, str]:
    if not text:
        return 0.0, "neutral"
    normalized = text.lower()
    pos_hits = sum(normalized.count(word) for word in POSITIVE_KEYWORDS)
    neg_hits = sum(normalized.count(word) for word in NEGATIVE_KEYWORDS)
    score = 0.0
    if pos_hits or neg_hits:
        score = (pos_hits - neg_hits) / max(pos_hits + neg_hits, 1)
    if score > 0.15:
        label = "positive"
    elif score < -0.15:
        label = "negative"
    else:
        label = "neutral"
    return score, label


def extract_symbols(text: str, valid_symbols: Set[str]) -> List[str]:
    if not text or not valid_symbols:
        return []
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, valid_symbols)) + r")\b")
    matches = pattern.findall(text.upper())
    seen = []
    for symbol in matches:
        if symbol == "HCM":
            continue
        if symbol not in seen:
            seen.append(symbol)
    return seen


def fetch_site_articles(
    site_name: str, limit: int, delay: float
) -> pd.DataFrame:
    logger.info("Fetching %s (limit=%s)", site_name, limit)
    crawler = Crawler(site_name=site_name)
    meta = crawler.get_articles(limit=limit)
    if not meta:
        logger.warning("No articles returned for %s", site_name)
        return pd.DataFrame()
    urls = [item.get("url") for item in meta if item.get("url")]
    if not urls:
        return pd.DataFrame()

    batch = BatchCrawler(site_name=site_name, request_delay=delay)
    details = batch.fetch_details_for_urls(urls=urls)
    if details is None or details.empty:
        logger.warning("No detail articles fetched for %s", site_name)
        return pd.DataFrame()
    details["source"] = site_name
    return details


def build_summary(
    df: pd.DataFrame, window_days: int, summary_path: Path
) -> None:
    summary: dict = {
        "generated_at": datetime.utcnow().isoformat(),
        "window_days": window_days,
        "article_count": int(len(df)),
        "sentiment": {
            "avg_score": float(df["sentiment_score"].mean())
            if not df.empty
            else 0.0,
            "positive": int((df["sentiment_label"] == "positive").sum()),
            "neutral": int((df["sentiment_label"] == "neutral").sum()),
            "negative": int((df["sentiment_label"] == "negative").sum()),
        },
        "top_sources": df["source"]
        .value_counts()
        .head(10)
        .to_dict(),
        "top_symbols": df["primary_symbol"]
        .dropna()
        .value_counts()
        .head(10)
        .to_dict(),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    logger.info("Wrote summary to %s", summary_path)


def persist_outputs(
    df: pd.DataFrame,
    raw_snapshot: Path,
    output_dir: Path,
    window_days: int,
) -> None:
    raw_snapshot.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_parquet(raw_snapshot, index=False)
    logger.info("Saved raw snapshot: %s", raw_snapshot)

    latest_path = output_dir / "news_latest.parquet"
    df.to_parquet(latest_path, index=False)
    logger.info("Saved processed dataset: %s", latest_path)

    summary_path = output_dir / "news_summary.json"
    build_summary(df, window_days=window_days, summary_path=summary_path)


def enrich_dataframe(df: pd.DataFrame, valid_symbols: Set[str]) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()

    text_cols = [
        col
        for col in ["title", "short_description", "summary", "markdown_content"]
        if col in df.columns
    ]
    if text_cols:
        df["combined_text"] = df[text_cols].fillna("").agg(" ".join, axis=1)
    else:
        df["combined_text"] = ""

    publish_col: Optional[str] = None
    for candidate in ["publish_time", "published_at", "date", "publishDate"]:
        if candidate in df.columns:
            publish_col = candidate
            break
    if publish_col is None:
        logger.warning("No publish_time column detected in news dataframe.")
        df["publish_time"] = pd.NaT
    else:
        df["publish_time"] = pd.to_datetime(df[publish_col], errors="coerce")
    df = df.dropna(subset=["publish_time"])

    df["symbols"] = df["combined_text"].apply(lambda text: extract_symbols(text, valid_symbols))
    df["primary_symbol"] = df["symbols"].apply(lambda items: items[0] if items else None)
    df["is_bsc_symbol"] = df["primary_symbol"].isin(valid_symbols)
    df["news_category"] = df["primary_symbol"].apply(
        lambda sym: "corporate" if isinstance(sym, str) else "market"
    )

    def _sentiment(row: pd.Series) -> tuple[float, str]:
        base_text = row.get("summary") or row.get("short_description") or row.get("combined_text")
        return compute_sentiment(str(base_text))

    sentiment_df = df.apply(lambda row: pd.Series(_sentiment(row)), axis=1)
    if not sentiment_df.empty:
        sentiment_df.columns = ["sentiment_score", "sentiment_label"]
        df["sentiment_score"] = sentiment_df["sentiment_score"]
        df["sentiment_label"] = sentiment_df["sentiment_label"]
    else:
        df["sentiment_score"] = 0.0
        df["sentiment_label"] = "neutral"

    df["importance"] = df["is_bsc_symbol"].map(lambda x: "High" if x else "Normal")
    df["publish_date"] = df["publish_time"].dt.date
    df = df.sort_values("publish_time", ascending=False).reset_index(drop=True)
    df = df.drop(columns=["combined_text"])
    return df


def main() -> None:
    args = parse_arguments()
    ensure_dependencies()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    valid_symbols = load_bsc_symbols()
    logger.info("Loaded %d BSC symbols", len(valid_symbols))

    collected = []
    for site in args.sites:
        try:
            site_df = fetch_site_articles(site, args.limit, args.delay)
            if not site_df.empty:
                collected.append(site_df)
        except Exception as exc:  # pragma: no cover - network errors
            logger.exception("Failed to fetch %s: %s", site, exc)
        finally:
            time.sleep(args.delay)

    if not collected:
        logger.error("No news collected. Abort.")
        sys.exit(1)

    df = pd.concat(collected, ignore_index=True)
    df = df[df["source"].isin(ECONOMIC_SOURCES)].copy()
    if df.empty:
        logger.error("All collected articles were filtered out due to source restrictions.")
        sys.exit(1)
    df = enrich_dataframe(df, valid_symbols=valid_symbols)
    if args.window_days:
        cutoff = datetime.utcnow() - timedelta(days=args.window_days)
        df = df[df["publish_time"] >= cutoff].copy()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    raw_snapshot = args.raw_dir / f"news_raw_{timestamp}.parquet"
    persist_outputs(
        df=df,
        raw_snapshot=raw_snapshot,
        output_dir=args.output_dir,
        window_days=args.window_days,
    )


if __name__ == "__main__":  # pragma: no cover
    main()

