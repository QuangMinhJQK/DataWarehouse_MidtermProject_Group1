"""Streamlit entrypoint for the Fabric semantic-model data agent."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from dataagent.agent_service import DataAgentService
from dataagent.config import get_settings
from dataagent.ui import inject_theme, render_assistant_message, render_hero

st.set_page_config(
    page_title="AdventureWorks Data Agent",
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


def load_health(service: DataAgentService) -> tuple[dict[str, Any] | None, str | None]:
    if "health_result" not in st.session_state:
        try:
            st.session_state.health_result = service.health_check()
            st.session_state.health_error = None
        except Exception as exc:
            st.session_state.health_result = None
            st.session_state.health_error = str(exc)
    return st.session_state.health_result, st.session_state.health_error


inject_theme()

try:
    service = get_service()
    health, health_error = load_health(service)
except Exception as exc:
    service = None
    health = None
    health_error = str(exc)

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
        st.success(f"Đã kết nối · {health.get('name')}")
        st.caption(f"Planner: `{health.get('planner_model')}`")
    else:
        st.error("Chưa sẵn sàng")
        if health_error:
            st.code(health_error, language="text")
    st.markdown("#### Câu hỏi mẫu")
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
        st.session_state.pop("health_error", None)
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
    user_message = {"role": "user", "text": prompt}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    compact_history = [
        {"role": item["role"], "text": item.get("text", "")}
        for item in st.session_state.messages[:-1]
    ][-6:]
    with st.chat_message("assistant"):
        with st.status("Lập kế hoạch → kiểm tra → truy vấn → diễn giải", expanded=False):
            response = service.answer(prompt, compact_history)
        assistant_message = {
            "role": "assistant",
            **response.model_dump(mode="json"),
        }
        render_assistant_message(assistant_message)
    st.session_state.messages.append(assistant_message)
