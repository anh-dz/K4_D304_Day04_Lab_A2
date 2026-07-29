# Hướng dẫn hoàn thiện và chạy Day 04 Lab v2

Project đã có UI, team eval và tool `calculator`, nhưng evidence chỉ hoàn thành
khi các lệnh provider/eval/live chat chạy thật. Không tự điền metric, hash hoặc
transcript trước khi có file JSON tương ứng.

## 1. Chuẩn bị trên Windows

Chạy trong Command Prompt hoặc PowerShell tại `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\preflight_provider.py --provider openrouter
```

Nếu dùng provider khác, thay `openrouter` bằng `gemini`, `openai` hoặc
`anthropic` trong tất cả lệnh. API key nằm trong `.env`; không commit, chụp màn
hình hoặc đưa file này vào bài nộp.

## 2. Smoke-test tool mới

```powershell
.\.venv\Scripts\python.exe -c "from tools import TOOL_FUNCTIONS as T; print(T['calculator']('math.sqrt(144)')); print(T['calculator']('math.pi * 5**2'))"
```

Hai kết quả phải không có lỗi và lần lượt xấp xỉ `12` và `78.539816`.

## 3. Chạy UI

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mở `http://localhost:8501`. Kiểm tra tối thiểu:

1. Một request research bình thường.
2. Một request thiếu thông tin rồi bổ sung ở lượt kế tiếp.
3. Một request gửi/post cần xác nhận yes/no.
4. Một phép tính dùng `calculator`.

UI tự lưu mỗi cuộc trò chuyện vào `transcripts/*.transcript.json`. Tab **Tool
trace** hiển thị từng round/call/result; tab **So sánh eval** chỉ đọc các run JSON
thật đã có trong `runs/`.

## 4. Quy trình eval bắt buộc

Không chạy bốn version liên tiếp trên cùng một `system_prompt.md` và
`tools.yaml`. Trước mỗi version phải có một hypothesis và một thay đổi artifact
thật; run JSON sẽ ghi hash để kiểm tra việc này.

### v0 — baseline

Dùng prompt và tool declarations nguyên bản của starter:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

### v1 — sửa hypothesis thứ nhất

Đọc failure của v0, sửa một vấn đề trong `artifacts/system_prompt.md` hoặc
`artifacts/tools.yaml`, rồi chạy:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
```

### v2 — sửa hypothesis thứ hai

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
```

### v3 — artifact cuối có calculator

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

Một run dùng làm evidence phải có:

```text
provider_error_cases = 0
measured_cases = total_cases
```

Routing PASS không chứng minh tool execution thành công. Phải kiểm tra thủ công
mọi `tool_results[*].result.error` trong run JSON.

## 5. Hoàn thiện file nộp

Sau khi có run thật:

- Điền đúng hash, hypothesis, metric trước/sau và tên run vào
  `artifacts/version_log.csv`.
- Thay toàn bộ placeholder trong `artifacts/REPORT.md` bằng evidence từ
  `runs/*.json` và `transcripts/*.transcript.json`.
- Kiểm tra đủ base `v0`, `v1`, `v2`, `v3` và group `v3`.
- Không nộp `.env`, `.venv/`, cache hoặc secret.
