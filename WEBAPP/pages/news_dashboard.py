from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from streamlit_app.layout.navigation import render_top_nav
from streamlit_app.services.news_loader import (
    compute_sentiment_overview,
    format_sentiment_label,
    load_news_data,
    load_news_summary,
    split_news_segments,
)

st.set_page_config(page_title="News Pulse Dashboard", layout="wide")


def render_sentiment_metrics(sentiment: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng số bài", sentiment.get("count", 0))
    with col2:
        st.metric("Điểm Sentiment TB", f"{sentiment.get('avg_score', 0.0):+.2f}")
    with col3:
        st.metric("Tích cực", sentiment.get("positive", 0))
    with col4:
        st.metric("Tiêu cực", sentiment.get("negative", 0))


def render_source_breakdown(df: pd.DataFrame) -> None:
    if df.empty or "source" not in df.columns:
        return
    counts = df["source"].value_counts().head(10).reset_index()
    counts.columns = ["source", "articles"]
    fig = px.bar(
        counts,
        x="articles",
        y="source",
        orientation="h",
        title="Top nguồn tin",
        text="articles",
        height=350,
    )
    fig.update_layout(yaxis_title="", xaxis_title="Số bài")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_sentiment_trend(df: pd.DataFrame) -> None:
    if df.empty or "publish_time" not in df.columns:
        return
    trend = (
        df.set_index("publish_time")
        .resample("6H")["sentiment_score"]
        .mean()
        .reset_index()
    )
    if trend.empty:
        return
    fig = px.line(
        trend,
        x="publish_time",
        y="sentiment_score",
        title="Xu hướng sentiment (6 giờ)",
    )
    fig.update_layout(
        xaxis_title="Thời gian",
        yaxis_title="Sentiment Score",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_news_cards(df: pd.DataFrame, limit: int = 12) -> None:
    subset = df.head(limit)
    for _, row in subset.iterrows():
        title = row.get("title") or row.get("headline") or "Chưa có tiêu đề"
        summary = (
            row.get("summary")
            or row.get("short_description")
            or (row.get("markdown_content") or "")[:280]
        )
        sentiment_label = format_sentiment_label(row.get("sentiment_label", "neutral"))
        timestamp = pd.to_datetime(
            row.get("publish_time"), errors="coerce", utc=True
        )
        time_str = ""
        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.tz_convert(None)
            time_str = timestamp.strftime("%H:%M %d/%m")
        meta_parts = [
            row.get("primary_symbol") or "Thị trường",
            row.get("source"),
            time_str,
            sentiment_label,
        ]
        meta = " • ".join([part for part in meta_parts if part])
        st.markdown(f"#### {title}")
        st.caption(meta)
        if summary:
            st.write(summary)
        if row.get("url"):
            st.markdown(f"[Đọc thêm]({row['url']})")
        st.divider()


def render_news_table(df: pd.DataFrame) -> None:
    if df.empty:
        return
    table_df = df[
        [
            col
            for col in [
                "publish_time",
                "source",
                "primary_symbol",
                "sentiment_label",
                "title",
            ]
            if col in df.columns
        ]
    ].copy()
    if "publish_time" in table_df.columns:
        publish_series = pd.to_datetime(
            table_df["publish_time"], errors="coerce", utc=True
        ).dt.tz_convert(None)
        table_df["publish_time"] = publish_series.dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
    )


def filter_dataframe(
    df: pd.DataFrame,
    sources: list[str],
    categories: list[str],
    symbols: list[str],
    require_bsc: bool,
) -> pd.DataFrame:
    filtered = df.copy()
    if sources:
        filtered = filtered[filtered["source"].isin(sources)]
    if categories:
        filtered = filtered[filtered["news_category"].isin(categories)]
    if symbols:
        filtered = filtered[filtered["primary_symbol"].isin(symbols)]
    if require_bsc:
        filtered = filtered[filtered.get("is_bsc_symbol", False)]
    return filtered


def main() -> None:
    render_top_nav()
    st.title("📰 News Pulse Dashboard")
    st.caption("Điểm tin thị trường & doanh nghiệp được cập nhật từ vnstock_news")

    reference_df = load_news_data(days=30)
    st.sidebar.header("Bộ lọc")
    days = st.sidebar.selectbox(
        "Khoảng thời gian",
        options=[1, 3, 7, 30],
        index=1,
        format_func=lambda d: f"{d} ngày gần nhất",
    )
    source_options = sorted(reference_df["source"].dropna().unique()) if not reference_df.empty else []
    selected_sources = st.sidebar.multiselect("Nguồn tin", options=source_options)

    category_options = ["market", "corporate"]
    selected_categories = st.sidebar.multiselect(
        "Nhóm tin",
        options=category_options,
        default=category_options,
    )

    symbol_options = sorted(reference_df["primary_symbol"].dropna().unique()) if not reference_df.empty else []
    selected_symbols = st.sidebar.multiselect("Mã cổ phiếu", options=symbol_options)
    require_bsc = st.sidebar.checkbox("Chỉ doanh nghiệp thuộc BSC coverage", value=False)

    with st.spinner("Đang tải dữ liệu..."):
        df = load_news_data(days=days)

    if df.empty:
        st.warning("Chưa có dữ liệu tin tức. Vui lòng chạy pipeline news trước.")
        return

    df = filter_dataframe(
        df=df,
        sources=selected_sources,
        categories=selected_categories,
        symbols=selected_symbols,
        require_bsc=require_bsc,
    )

    if df.empty:
        st.info("Không có bài viết phù hợp với bộ lọc.")
        return

    sentiment = compute_sentiment_overview(df)
    render_sentiment_metrics(sentiment)

    summary_payload = load_news_summary()
    if summary_payload:
        with st.expander("📌 Snapshot pipeline", expanded=False):
            st.write(
                f"Dataset cập nhật: {summary_payload.get('generated_at', 'N/A')} "
                f"• Tổng bài: {summary_payload.get('article_count', 0)}"
            )
            top_sources = summary_payload.get("top_sources", {})
            if top_sources:
                st.write("Nguồn nổi bật:", ", ".join(f"{k} ({v})" for k, v in top_sources.items()))
            top_symbols = summary_payload.get("top_symbols", {})
            if top_symbols:
                st.write("Mã được nhắc nhiều:", ", ".join(f"{k} ({v})" for k, v in top_symbols.items()))

    col_left, col_right = st.columns(2)
    with col_left:
        render_source_breakdown(df)
    with col_right:
        render_sentiment_trend(df)

    market_df, bsc_df, other_df = split_news_segments(df)

    tab_market, tab_bsc, tab_other = st.tabs(
        [
            "🌐 Điểm tin thị trường",
            "🏢 Doanh nghiệp thuộc BSC",
            "📁 Doanh nghiệp khác",
        ]
    )

    with tab_market:
        st.subheader("🌐 Điểm tin thị trường")
        if market_df.empty:
            st.info("Chưa có tin thị trường trong phạm vi đã chọn.")
        else:
            render_news_cards(market_df)
            render_news_table(market_df)

    with tab_bsc:
        st.subheader("🏢 Doanh nghiệp BSC Coverage")
        if bsc_df.empty:
            st.info("Không có tin doanh nghiệp thuộc coverage BSC trong phạm vi này.")
        else:
            render_news_cards(bsc_df)
            render_news_table(bsc_df)

    with tab_other:
        st.subheader("📁 Doanh nghiệp còn lại")
        if other_df.empty:
            st.info("Không có tin doanh nghiệp ngoài coverage BSC trong phạm vi này.")
        else:
            render_news_cards(other_df)
            render_news_table(other_df)


if __name__ == "__main__":
    main()

