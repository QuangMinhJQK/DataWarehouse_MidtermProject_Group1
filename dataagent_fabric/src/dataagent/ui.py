"""Streamlit rendering helpers kept separate from orchestration logic."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;650;750&display=swap');
        :root {
          --ink: #13231f;
          --paper: #f4f0e7;
          --forest: #123f36;
          --mint: #99f2c8;
          --rust: #d9633b;
          --line: rgba(19, 35, 31, .16);
        }
        html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
        .stApp {
          background:
            linear-gradient(rgba(18,63,54,.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(18,63,54,.035) 1px, transparent 1px),
            var(--paper);
          background-size: 26px 26px;
          color: var(--ink);
        }
        .block-container { max-width: 1040px; padding-top: 2.1rem; }
        .hero {
          border: 1px solid var(--ink);
          background: var(--forest);
          color: #f7f3ea;
          padding: 1.5rem 1.7rem 1.35rem;
          box-shadow: 8px 8px 0 #b7d8c8;
          margin-bottom: 1.6rem;
        }
        .hero-kicker, .mono { font-family: 'DM Mono', monospace; }
        .hero-kicker {
          color: var(--mint);
          letter-spacing: .12em;
          font-size: .75rem;
          text-transform: uppercase;
        }
        .hero h1 {
          font-size: clamp(2rem, 5vw, 3.6rem);
          line-height: .98;
          margin: .5rem 0 .75rem;
          letter-spacing: -.05em;
        }
        .hero p { max-width: 720px; margin: 0; opacity: .82; }
        .status-strip { display:flex; gap:.55rem; flex-wrap:wrap; margin-top:1rem; }
        .status-chip {
          border:1px solid rgba(255,255,255,.28);
          padding:.28rem .55rem;
          font-family:'DM Mono',monospace;
          font-size:.7rem;
        }
        [data-testid="stChatMessage"] {
          border: 1px solid var(--line);
          background: rgba(255,255,255,.48);
          padding: .45rem .7rem;
        }
        [data-testid="stChatInput"] { border: 1px solid var(--ink); box-shadow: 4px 4px 0 #b7d8c8; }
        [data-testid="stSidebar"] { border-right: 1px solid var(--ink); background: #e8e2d7; }
        .warning-note {
          border-left: 4px solid var(--rust);
          padding: .45rem .7rem;
          background: rgba(217,99,59,.09);
          margin:.35rem 0;
        }
        div[data-testid="stMetric"] { border:1px solid var(--line); padding:.5rem; }
        code, pre { font-family: 'DM Mono', monospace !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(health: dict[str, Any] | None) -> None:
    if health:
        chips = (
            f'<span class="status-chip">MODEL · {health.get("name")}</span>'
            f'<span class="status-chip">CATALOG · {health.get("catalog_version")}</span>'
            '<span class="status-chip">MODE · READ ONLY</span>'
        )
    else:
        chips = '<span class="status-chip">CONNECTION · UNAVAILABLE</span>'
    st.markdown(
        f"""
        <section class="hero">
          <div class="hero-kicker">AdventureWorks · Semantic Control Room</div>
          <h1>Ask the model.<br/>Keep the metric.</h1>
          <p>
            Trợ lý hỏi đáp trực tiếp trên Fabric Semantic Model.
            Mọi truy vấn đều qua catalog allowlist và DAX compiler chỉ đọc.
          </p>
          <div class="status-strip">{chips}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_assistant_message(message: dict[str, Any]) -> None:
    st.markdown(message.get("text", ""))
    rows = message.get("rows") or []
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    for warning in message.get("warnings") or []:
        st.markdown(f'<div class="warning-note">{warning}</div>', unsafe_allow_html=True)
    with st.expander("Chi tiết truy vấn · audit"):
        st.caption(f"Request ID: {message.get('request_id', 'n/a')}")
        if message.get("query_plan"):
            st.json(message["query_plan"])
        if message.get("dax"):
            st.code(message["dax"], language="text")
