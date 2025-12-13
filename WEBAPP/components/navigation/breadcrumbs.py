"""
Breadcrumb Component
====================

Breadcrumb trail for navigation hierarchy.

Author: AI Assistant
Date: 2025-12-12
"""

import streamlit as st
from typing import List


def render_breadcrumbs(items: List[str]):
    """
    Render breadcrumb trail.

    Args:
        items: List of breadcrumb items (e.g., ["Home", "Fundamental", "Company"])

    Usage:
        from WEBAPP.components.navigation import render_breadcrumbs

        render_breadcrumbs(["Home", "Fundamental Analysis", "Company Analysis"])
    """
    if not items:
        return

    breadcrumb_html = " > ".join([f"<span>{item}</span>" for item in items])

    st.markdown(f"""
    <style>
    .breadcrumbs {{
        font-size: 0.875rem;
        color: #6B7280;
        margin-bottom: 1rem;
    }}
    .breadcrumbs span {{
        margin: 0 0.25rem;
    }}
    </style>
    <div class="breadcrumbs">
        {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)
