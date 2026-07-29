---
name: wiki_search
track: core
kind: live_api
provider: Wikipedia
requires_env: []
inputs: [title]
outputs: [summary]
side_effect: false
requires_confirmation: false
---

# wiki_search

Tìm kiếm thông tin tóm tắt trên Wikipedia tiếng Anh về một chủ đề, thực thể, sự kiện lịch sử hoặc khái niệm cụ thể.

## Inputs
- `title` (string): Tiêu đề hoặc từ khóa chính xác của trang Wikipedia (ví dụ: "Artificial intelligence", "Python (programming language)", "World War II").

## Outputs
- `summary` (string): Nội dung tóm tắt ngắn gọn của bài viết trên Wikipedia.
