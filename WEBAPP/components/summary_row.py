"""Summary row component (bilingual / song ngữ)

Render a horizontal row of metrics: Current P/E, P/B, EV/EBITDA, Overall.

VN: Hàng tóm tắt các chỉ số hiện tại và xếp hạng tổng hợp.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd


def render_summary_row(current_pe: float | None,
                       pe_pct: float | None,
                       current_pb: float | None,
                       pb_pct: float | None,
                       current_ev: float | None,
                       ev_pct: float | None,
                       overall_label: str,
                       overall_pct: float | None) -> None:
    """Render 4 metric cards in one row.

    VN: Hiển thị 4 thẻ chỉ số trên một hàng (P/E, P/B, EV/EBITDA, Overall).
    """
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        st.metric("Current P/E", f"{current_pe:.2f}" if current_pe is not None else "-",
                  f"{pe_pct:.0f}th pct" if pe_pct is not None else "")
    with c2:
        st.metric("Current P/B", f"{current_pb:.2f}" if current_pb is not None else "-",
                  f"{pb_pct:.0f}th pct" if pb_pct is not None else "")
    with c3:
        st.metric("Current EV/EBITDA", f"{current_ev:.2f}" if current_ev is not None else "-",
                  f"{ev_pct:.0f}th pct" if ev_pct is not None else "")
    with c4:
        st.metric("Overall Valuation", overall_label or "N/A",
                  f"{overall_pct:.0f}th pct" if overall_pct is not None else "")

    st.caption("Percentiles calculated vs own 5-year history. Outliers removed (P/E>100, P/B>10, EV/EBITDA>100)")


