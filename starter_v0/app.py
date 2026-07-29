import streamlit as st
import json
from pathlib import Path

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent Eval UI", layout="wide")

st.title("Research Agent - Lab Day 04 v2")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    provider_name = st.selectbox("Provider", ["gemini", "openrouter", "openai", "anthropic"], index=0)
    version = st.text_input("Version (e.g. v3)", value="v3")
    max_tool_rounds = st.number_input("Max Tool Rounds", min_value=1, max_value=10, value=4)

if "history" not in st.session_state:
    st.session_state.history = []

if "tool_events" not in st.session_state:
    st.session_state.tool_events = []

# Load system prompt and tools
try:
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    artifact_version = build_artifact_version(version, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")
    
    st.sidebar.success(f"Loaded {len(openai_tools)} tools.")
    st.sidebar.text(f"Artifact Hash:\n{artifact_version.artifact_version}")
except Exception as e:
    st.sidebar.error(f"Config error: {e}")
    st.stop()

# Main Chat Interface
chat_container = st.container()

with chat_container:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_text = st.chat_input("Nhập câu hỏi của bạn...")

if user_text:
    # 1. Add user message
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 2. Setup messages
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history[:-1], 5),
        {"role": "user", "content": user_text},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=max_tool_rounds,
                )
                
                assistant_text = result.get("assistant_text", "")
                events = result.get("tool_events", [])
                
                st.markdown(assistant_text)
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                
                if events:
                    with st.expander("Tool Trace", expanded=False):
                        for event in events:
                            st.write(f"**Tool:** `{event['tool']}`")
                            st.json(event["args"])
                            st.write("**Result:**")
                            st.json(event["result"])
                            st.divider()

            except Exception as e:
                st.error(f"Lỗi: {e}")

if st.sidebar.button("Clear Chat"):
    st.session_state.history = []
    st.session_state.tool_events = []
    st.rerun()
