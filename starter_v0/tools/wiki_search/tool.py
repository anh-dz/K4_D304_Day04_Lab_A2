from __future__ import annotations

import requests
from typing import Any
from tools._shared import err

def wiki_search(title: str = "") -> dict[str, Any]:
    if not title:
        return {"tool": "wiki_search", "error": "MissingTitle", "message": "Vui lòng cung cấp tiêu đề cần tìm kiếm."}
    
    # URL encoded title name
    formatted_title = title.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"
    
    try:
        headers = {
            "User-Agent": "ResearchAgent/1.0 (educational lab; contact: user@example.com)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return {
                "tool": "wiki_search",
                "title": title,
                "error": "NotFound",
                "message": f"Không tìm thấy trang Wikipedia cho chủ đề '{title}'."
            }
            
        response.raise_for_status()
        data = response.json()
        
        summary = data.get("extract") or data.get("description") or "Không có nội dung tóm tắt khả dụng."
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        
        return {
            "tool": "wiki_search",
            "title": title,
            "summary": summary,
            "url": page_url
        }
    except Exception as exc:
        return err("wiki_search", exc)
