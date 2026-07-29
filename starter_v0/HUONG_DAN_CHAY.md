# Tổng kết công việc & Hướng dẫn sử dụng (Day 04 Lab v2)

## 1. Những gì mình đã làm để hoàn thành Lab

Mình đã hoàn thiện toàn bộ mã nguồn và cấu hình theo đúng chuẩn yêu cầu của Lab Day 04, bao gồm:

- **Tạo mới Tool `calculator`**: 
  - Đã thêm tool này vào `tools/calculator/tool.py` (tính toán an toàn với Python `math`).
  - Đã đăng ký nó vào `tools/__init__.py` và `artifacts/tools.yaml`.
- **Viết 10 Team Eval Cases**: 
  - Hoàn thành đầy đủ 5 cases hội thoại đơn (single-turn) và 5 cases đa lượt (multi-turn) trong file `data/eval_group.json`. Các case này test rất đa dạng kỹ năng (thử logic đổi tool, clarify lại URL, hỏi xác nhận trước khi đăng bài,...).
- **Tối ưu hóa Prompts & Tool declarations (Phiên bản v3)**: 
  - Sửa đổi `artifacts/system_prompt.md` cực kỳ chặt chẽ: Yêu cầu AI luôn dùng `clarify` (không được tự đoán bừa) nếu thiếu dữ kiện và bắt buộc hỏi yes/no trước hành động nhạy cảm như gửi tin nhắn.
  - Sửa đổi `artifacts/tools.yaml` giúp AI hiểu rõ các ranh giới và cách nhận diện từ khóa "hôm nay", "tuần này" hoặc tìm kiếm "phổ biến".
- **Xây dựng UI Chatbot (Streamlit)**: 
  - Đã lập trình file `app.py` với giao diện web, tích hợp đầy đủ lịch sử chat và chức năng theo dõi "Tool Trace" (để xem log các arguments mà AI truyền vào tool).
- **Dự thảo Report & Version Log**: 
  - Khung báo cáo nộp bài `artifacts/REPORT.md` và file log `artifacts/version_log.csv` đã được tạo sẵn để bạn điền số liệu.

---

## 2. Hướng dẫn chạy sản phẩm

Bạn hãy thực hiện tuần tự các bước dưới đây để chạy thử:

### Bước 1: Khai báo API Key
App cần có API Key để mô hình ngôn ngữ (Gemini, OpenRouter, v.v.) hoạt động. 
1. Tại thư mục `starter_v0`, tạo một file mới tên là `.env` (nếu chưa có). Bạn có thể copy từ `.env.example`.
2. Mở file `.env` lên và điền Key vào. Ví dụ nếu bạn dùng Gemini:
   ```text
   GEMINI_API_KEY=AIzaSy...dán_key_của_bạn_vào_đây...
   ```
   *(Lưu ý: Không dùng ngoặc kép bao quanh key)*

### Bước 2: Khởi chạy giao diện Chat (UI)
1. Mở Terminal tại thư mục `starter_v0`.
2. Chạy lệnh kích hoạt môi trường ảo (nếu bạn cài packages vào venv):
   ```bash
   source venv/bin/activate
   ```
3. Khởi động Streamlit:
   ```bash
   streamlit run app.py
   ```
4. Trình duyệt sẽ tự động mở trang `http://localhost:8501`. Tại đây, bạn có thể gõ câu hỏi (Ví dụ: *"Tính giúp tôi 15% của 800"* hoặc *"Hôm nay AI có gì mới?"*) để test khả năng phản hồi và xem Tool Trace của Agent.

### Bước 3: Chạy Evaluation tự động (Để lấy file JSON Log chấm điểm)
Trong quá trình nộp bài, bạn bắt buộc phải có log của các eval cases. Hãy mở một tab Terminal mới và chạy các lệnh sau (Đảm bảo đã khai báo API Key):

**Chạy Base Eval (v0):**
```bash
python run_eval.py --provider gemini --version v0 --suite base --eval-cases data/eval_base.json
```

**Chạy Group Eval (10 cases nhóm tự viết - v3):**
```bash
python run_eval.py --provider gemini --version v3 --suite group --eval-cases data/eval_group.json
```

Kết quả chấm (pass/fail) sẽ in ra ở Terminal và log JSON đầy đủ được lưu trong thư mục `runs/`. Bạn hãy lấy điểm số `accuracy` từ màn hình console này điền vào file `version_log.csv` và `REPORT.md` để nộp bài nhé!
