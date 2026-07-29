from __future__ import annotations

from typing import Any

from tools._shared import err

# Maintainable directory of well-known display names -> canonical handles.
# This replaces hardcoding the mapping inline in the system prompt, so the
# list can grow without editing prompt text or risking the model guessing.
_KNOWN_HANDLES: dict[str, str] = {
    "sam altman": "sama",
    "elon musk": "elonmusk",
    "andrej karpathy": "karpathy",
    "bill gates": "BillGates",
    "satya nadella": "satyanadella",
    "sundar pichai": "sundarpichai",
}


def resolve_handle(display_name: str = "") -> dict[str, Any]:
    try:
        name = (display_name or "").strip()
        if not name:
            raise ValueError("display_name is required")
        handle = _KNOWN_HANDLES.get(name.lower())
        return {
            "tool": "resolve_handle",
            "display_name": name,
            "handle": handle,
            "found": handle is not None,
        }
    except Exception as exc:
        return err("resolve_handle", exc)
