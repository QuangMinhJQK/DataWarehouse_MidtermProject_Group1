"""Streamlit dashboard and public, read-only Fabric data agent."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Community Cloud installs requirements but does not install this local package.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dataagent.agent_service import DataAgentService  # noqa: E402
from dataagent.config import get_settings  # noqa: E402
from dataagent.ui import inject_theme, render_assistant_message, render_hero  # noqa: E402

REPORT_URL = (
    "https://app.fabric.microsoft.com/view?"
    "r=eyJrIjoiOWM2M2ZiOGEtOGE1YS00NDU0LWI4ZDgtNGM0MGMyN2YwNzEwIiwidCI6"
    "IjExOGQ0NmZmLTkxZDUtNDhkNS1iOWI3LWEwMTA4ZTI4ZTliMyIsImMiOjEwfQ%3D%3D"
    "&pageName=b0e897342a58048000e3"
)

st.set_page_config(
    page_title="AdventureWorks | Dashboard & Data Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def get_service() -> DataAgentService:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return DataAgentService(settings=settings)


def load_health(service: DataAgentService) -> tuple[dict[str, Any] | None, bool]:
    if "health_result" not in st.session_state:
        try:
            st.session_state.health_result = service.health_check()
            st.session_state.health_failed = False
        except Exception:
            logging.getLogger(__name__).warning("Data Agent health check failed")
            st.session_state.health_result = None
            st.session_state.health_failed = True
    return st.session_state.health_result, st.session_state.health_failed


def render_dashboard() -> None:
    st.title("Dashboard vận hành")
    st.caption("Báo cáo Power BI/Fabric được công bố công khai.")
    st.link_button("Mở dashboard trong tab mới", REPORT_URL)
    st.iframe(REPORT_URL, height=760)


def render_agent() -> None:
    try:
        service = get_service()
        health, health_failed = load_health(service)
    except Exception:
        logging.getLogger(__name__).warning("Data Agent initialization failed")
        service, health, health_failed = None, None, True

    render_hero(health)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    examples = [
        "Doanh thu thuần và số đơn theo năm là bao nhiêu?",
        "Top 5 danh mục sản phẩm theo doanh thu thuần.",
        "Tỷ lệ giao trễ theo khu vực là bao nhiêu?",
        "Có bao nhiêu sản phẩm cần đặt lại và snapshot tồn kho lúc nào?",
    ]

    with st.sidebar:
        st.markdown("### Query desk")
        if health:
            st.success("Đã kết nối Semantic Model")
        elif health_failed:
            st.error("Data Agent chưa sẵn sàng. Kiểm tra cấu hình và quyền API trên máy chủ.")
        selected_example = None
        for index, example in enumerate(examples):
            if st.button(example, key=f"example_{index}", width="stretch"):
                selected_example = example
        st.divider()
        if st.button("Xóa hội thoại", width="stretch"):
            st.session_state.messages = []
            st.rerun()
        if st.button("Kiểm tra lại kết nối", width="stretch"):
            st.session_state.pop("health_result", None)
            st.session_state.pop("health_failed", None)
            st.rerun()
        st.caption("Read-only · Aggregate-first · No raw DAX from the LLM")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_assistant_message(message)
            else:
                st.markdown(message["text"])

    typed_prompt = st.chat_input(
        "Hỏi về doanh thu, đơn hàng, sản phẩm, tồn kho hoặc forecast…",
        disabled=service is None or health is None,
    )
    prompt = typed_prompt or selected_example

    if prompt and service is not None and health is not None:
        st.session_state.messages.append({"role": "user", "text": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        compact_history = [
            {"role": item["role"], "text": item.get("text", "")}
            for item in st.session_state.messages[:-1]
        ][-6:]
        with st.chat_message("assistant"):
            with st.status("Lập kế hoạch → kiểm tra → truy vấn → diễn giải", expanded=False):
                response = service.answer(prompt, compact_history)
            assistant_message = {"role": "assistant", **response.model_dump(mode="json")}
            render_assistant_message(assistant_message)
        st.session_state.messages.append(assistant_message)


inject_theme()
with st.sidebar:
    page = st.radio("Điều hướng", ["Dashboard", "Data Agent"], label_visibility="collapsed")

if page == "Dashboard":
    render_dashboard()
else:
    render_agent()
