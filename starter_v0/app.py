from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"

load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent Eval UI",
    page_icon="🔎",
    layout="wide",
)


_SENSITIVE_KEY = re.compile(r"api[_-]?key|token|authorization|secret|password", re.IGNORECASE)
_SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:or-)?[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{10,}"),
)


def redact_text(value: str) -> str:
    redacted = value
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("<redacted>", redacted)
    return redacted


def safe_value(value: Any) -> Any:
    """Return a JSON-safe copy with likely secrets removed."""
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            result[key_text] = "<redacted>" if _SENSITIVE_KEY.search(key_text) else safe_value(item)
        return result
    if isinstance(value, list):
        return [safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [safe_value(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return redact_text(str(value))


def new_transcript(
    *,
    provider_name: str,
    selected_model: str | None,
    version: str,
    artifact: Any,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[dict[str, Any], Path, str]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join((safe_slug(version), safe_slug(provider_name), timestamp))
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    config_signature = "|".join(
        (
            artifact.artifact_version,
            provider_name,
            selected_model or "default",
            str(history_window),
            str(max_tool_rounds),
        )
    )
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, transcript_path, config_signature


def reset_conversation() -> None:
    st.session_state.history = []
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.config_signature = None


def load_run(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tool_error_count(run: dict[str, Any]) -> int:
    count = 0
    for case in run.get("results", []):
        for event in case.get("tool_results", []) or []:
            result = event.get("result")
            if isinstance(result, dict) and result.get("error"):
                count += 1
    return count


def default_run_selection(run_records: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    latest: dict[tuple[str, str], tuple[str, str]] = {}
    for path, run in run_records:
        key = (str(run.get("version", "?")), str(run.get("suite", "?")))
        generated_at = str(run.get("generated_at", ""))
        if key not in latest or generated_at > latest[key][0]:
            latest[key] = (generated_at, path.name)
    return [item[1] for item in latest.values()]


for key, default in (
    ("history", []),
    ("transcript", None),
    ("transcript_path", None),
    ("config_signature", None),
):
    if key not in st.session_state:
        st.session_state[key] = default


try:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
except Exception as exc:
    st.error(f"Không thể tải artifacts: {redact_text(str(exc))}")
    st.stop()


st.title("🔎 Research Agent")
st.caption("Chat thật · tool trace theo round · transcript JSON · so sánh eval theo version")

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox(
        "Provider",
        ["openrouter", "gemini", "openai", "anthropic"],
        index=0,
    )
    model_input = st.text_input("Model (để trống dùng mặc định)", value="").strip()
    version = st.text_input("Artifact version", value="v3").strip() or "v3"
    history_window = int(st.number_input("Số cặp hội thoại giữ lại", 1, 20, 5))
    max_tool_rounds = int(st.number_input("Số tool round tối đa", 1, 10, 4))

    artifact = build_artifact_version(version, system_prompt_path, tools_path)
    st.divider()
    st.subheader("Artifact đang dùng")
    st.code(artifact.artifact_version, language=None)
    st.caption(f"Prompt hash: `{artifact.prompt_hash}`")
    st.caption(f"Tools hash: `{artifact.tools_hash}`")
    st.caption(f"Đã khai báo {len(openai_tools)} tools")

    if st.button("Cuộc trò chuyện mới", use_container_width=True):
        reset_conversation()
        st.rerun()

    transcript = st.session_state.transcript
    transcript_path = st.session_state.transcript_path
    if transcript and transcript_path:
        st.download_button(
            "Tải transcript JSON",
            data=json.dumps(safe_value(transcript), ensure_ascii=False, indent=2),
            file_name=Path(transcript_path).name,
            mime="application/json",
            use_container_width=True,
        )
        st.caption(f"Đã lưu: `transcripts/{Path(transcript_path).name}`")


chat_tab, trace_tab, runs_tab = st.tabs(("💬 Chat", "🧰 Tool trace", "📊 So sánh eval"))

with chat_tab:
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input("Nhập yêu cầu research hoặc phép tính...")
    if user_text:
        raw_user_text = user_text.strip()
        if raw_user_text:
            with st.spinner("Agent đang gọi model và tool..."):
                try:
                    provider = make_provider(provider_name)
                    selected_model = model_input or getattr(provider, "default_model", None)
                    desired_signature = "|".join(
                        (
                            artifact.artifact_version,
                            provider_name,
                            selected_model or "default",
                            str(history_window),
                            str(max_tool_rounds),
                        )
                    )

                    if (
                        st.session_state.transcript is None
                        or st.session_state.config_signature != desired_signature
                    ):
                        transcript, transcript_path, signature = new_transcript(
                            provider_name=provider_name,
                            selected_model=selected_model,
                            version=version,
                            artifact=artifact,
                            history_window=history_window,
                            max_tool_rounds=max_tool_rounds,
                        )
                        st.session_state.transcript = transcript
                        st.session_state.transcript_path = transcript_path
                        st.session_state.config_signature = signature
                        st.session_state.history = []

                    turn_index = len(st.session_state.transcript["turns"]) + 1
                    turn_record: dict[str, Any] = {
                        "turn_index": turn_index,
                        "started_at": now_iso(),
                        "user": redact_text(raw_user_text),
                        "status": "started",
                        "assistant_text": None,
                        "rounds": [],
                        "tool_events": [],
                    }

                    messages = [
                        {"role": "system", "content": system_prompt},
                        *trim_history(st.session_state.history, history_window),
                        {"role": "user", "content": raw_user_text},
                    ]

                    try:
                        result = run_model_tool_loop(
                            provider=provider,
                            messages=messages,
                            tools=openai_tools,
                            model=model_input or None,
                            max_tool_rounds=max_tool_rounds,
                        )
                        clean_result = safe_value(result)
                        turn_record.update(clean_result)
                        assistant_text = str(clean_result.get("assistant_text", ""))
                    except Exception as exc:
                        assistant_text = f"Provider gặp lỗi: {redact_text(str(exc))}"
                        turn_record.update(
                            {
                                "status": "provider_error",
                                "assistant_text": assistant_text,
                                "error": f"{type(exc).__name__}: {redact_text(str(exc))}",
                            }
                        )

                    turn_record["ended_at"] = now_iso()
                    st.session_state.transcript["turns"].append(turn_record)
                    st.session_state.history.append(
                        {"role": "user", "content": redact_text(raw_user_text)}
                    )
                    st.session_state.history.append(
                        {"role": "assistant", "content": assistant_text}
                    )
                    st.session_state.transcript["updated_at"] = now_iso()
                    write_transcript(
                        Path(st.session_state.transcript_path),
                        safe_value(st.session_state.transcript),
                    )
                except Exception as exc:
                    st.error(f"Không thể khởi tạo provider: {redact_text(str(exc))}")
                else:
                    st.rerun()

    if not st.session_state.history:
        st.info(
            "Thử: “Tin AI hôm nay có gì?”, “Tóm tắt bài này giúp mình”, "
            "hoặc “Tính 15% của 25000”."
        )


with trace_tab:
    transcript = st.session_state.transcript
    if not transcript or not transcript.get("turns"):
        st.info("Chưa có tool trace. Hãy gửi một yêu cầu trong tab Chat.")
    else:
        st.caption(
            f"Transcript `{transcript['transcript_id']}` · "
            f"Artifact `{transcript['artifact_version']}`"
        )
        for turn in reversed(transcript["turns"]):
            status = turn.get("status", "unknown")
            label = f"Turn {turn.get('turn_index')} · {status} · {turn.get('user', '')[:70]}"
            with st.expander(label, expanded=turn is transcript["turns"][-1]):
                st.markdown(f"**User:** {turn.get('user', '')}")
                st.markdown(f"**Assistant:** {turn.get('assistant_text') or '—'}")
                if turn.get("error"):
                    st.error(str(turn["error"]))

                rounds = turn.get("rounds", []) or []
                if not rounds:
                    st.caption("Turn này không có model/tool round được ghi lại.")
                for round_record in rounds:
                    st.markdown(f"#### Round {round_record.get('round', '?')}")
                    if round_record.get("assistant_text"):
                        st.caption(str(round_record["assistant_text"]))

                    calls = round_record.get("tool_calls", []) or []
                    results = round_record.get("tool_results", []) or []
                    if not calls:
                        st.write("Không gọi tool trong round này.")
                    for index, call in enumerate(calls):
                        event = results[index] if index < len(results) else {}
                        left, right = st.columns(2)
                        with left:
                            st.markdown(f"**Tool:** `{call.get('name', '?')}`")
                            st.caption("Arguments")
                            st.json(safe_value(call.get("args", {})))
                        with right:
                            result = event.get("result", {}) if isinstance(event, dict) else {}
                            if isinstance(result, dict) and result.get("error"):
                                st.error(f"{result.get('error')}: {result.get('message', '')}")
                            st.caption("Result")
                            st.json(safe_value(result))


with runs_tab:
    if not RUNS_DIR.exists():
        st.info("Chưa có thư mục `runs/`. Hãy chạy `run_eval.py` để tạo evidence thật.")
    else:
        run_records: list[tuple[Path, dict[str, Any]]] = []
        invalid_runs: list[str] = []
        for path in sorted(RUNS_DIR.glob("*.json")):
            try:
                run_records.append((path, load_run(path)))
            except Exception:
                invalid_runs.append(path.name)

        if invalid_runs:
            st.warning("Không đọc được: " + ", ".join(invalid_runs))
        if not run_records:
            st.info("Chưa có run JSON hợp lệ.")
        else:
            files_by_name = {path.name: (path, run) for path, run in run_records}
            selected_names = st.multiselect(
                "Chọn run để so sánh",
                options=list(files_by_name),
                default=default_run_selection(run_records),
            )
            selected_runs = [files_by_name[name] for name in selected_names]

            if not selected_runs:
                st.info("Chọn ít nhất một run JSON.")
            else:
                summary_rows = []
                for path, run in selected_runs:
                    summary = run.get("summary", {})
                    total = summary.get("total_cases")
                    measured = summary.get("measured_cases")
                    provider_errors = summary.get("provider_error_cases")
                    summary_rows.append(
                        {
                            "file": path.name,
                            "version": run.get("version"),
                            "suite": run.get("suite"),
                            "artifact_version": run.get("artifact_version"),
                            "case_accuracy": summary.get("case_accuracy"),
                            "routing_accuracy": summary.get("tool_routing_accuracy"),
                            "argument_accuracy": summary.get("argument_accuracy"),
                            "multiturn_accuracy": summary.get("multiturn_accuracy"),
                            "measured": f"{measured}/{total}",
                            "provider_errors": provider_errors,
                            "tool_errors": tool_error_count(run),
                            "metric_valid": provider_errors == 0 and measured == total,
                        }
                    )
                st.dataframe(summary_rows, use_container_width=True, hide_index=True)

                case_ids = sorted(
                    {
                        str(case.get("id"))
                        for _, run in selected_runs
                        for case in run.get("results", [])
                        if case.get("id")
                    }
                )
                if case_ids:
                    selected_case_id = st.selectbox("So sánh cùng một case", case_ids)
                    for path, run in selected_runs:
                        case = next(
                            (
                                item
                                for item in run.get("results", [])
                                if item.get("id") == selected_case_id
                            ),
                            None,
                        )
                        with st.expander(
                            f"{run.get('version', '?')} · {path.name}",
                            expanded=len(selected_runs) <= 3,
                        ):
                            if case is None:
                                st.caption("Case không xuất hiện trong run này.")
                                continue
                            result = case.get("result", {})
                            st.write(
                                {
                                    "passed": result.get("passed"),
                                    "observed_mismatch": result.get("observed_mismatch"),
                                    "failures": safe_value(result.get("failures", [])),
                                }
                            )
                            st.caption("Expected")
                            st.json(safe_value(case.get("expect", {})))
                            st.caption("Actual tool calls")
                            st.json(safe_value(result.get("actual_tool_calls", [])))
