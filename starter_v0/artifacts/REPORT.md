# Day 04 Lab v2 Report — Research Agent

## Phần A: Giới thiệu chung (Dùng cho Demo)

### 1. Agent Name & Mục tiêu
- **Tên Agent**: Research & Calculation Agent (Group X)
- **Mục tiêu**: Hỗ trợ tìm kiếm thông tin, tra cứu tin tức, phân tích mạng xã hội và thực hiện tính toán.

### 2. Các công cụ (Tools) nổi bật
- **Core Tools**: `clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `format`
- **Optional Tools**: `send`, `policy`, `papers`, `paper_text`
- **🔥 Tool mới được thêm**: `calculator` (Hỗ trợ tính toán biểu thức toán học và gọi hàm trong thư viện `math` của Python)

### 3. Cách chạy Demo
```bash
# Bật Streamlit UI
streamlit run app.py
```
*(Nếu cần URL chia sẻ: `cloudflared tunnel --url http://localhost:8501`)*

### 4. Câu hỏi thử nghiệm tiêu biểu
- "Tính diện tích hình tròn có bán kính 5"
- "Tin AI hôm nay có gì nổi bật?"
- "Đăng bài này lên nhóm nhé" -> (Agent sẽ tự động hỏi xác nhận)


---

## Phần B: Bằng chứng & Phân tích chi tiết

### 1. Version Log (Tóm tắt từ `version_log.csv`)
| Version | Mục tiêu cải tiến | Kết quả (Metric: routing_accuracy) |
| --- | --- | --- |
| `v0` (Baseline) | Chạy thử nghiệm ban đầu | (Điền số liệu sau khi chạy run_eval) |
| `v1` | Tối ưu prompt, bổ sung nguyên tắc hỏi lại handle | (Điền số liệu sau khi chạy run_eval) |
| `v2` | Khắc phục ranh giới xác nhận (boundary) cho tool send | (Điền số liệu sau khi chạy run_eval) |
| `v3` | Cấu trúc lại tools.yaml, thêm Calculator tool | (Điền số liệu sau khi chạy run_eval) |

### 2. Failure Analysis
- **Vấn đề v0**: Agent thường tự đoán URL hoặc tự gửi Telegram mà không hỏi xác nhận. 
- **Cách giải quyết (v3)**: Thêm mô tả chặt chẽ cho tool `clarify` và `send`, yêu cầu dùng `yes_no` để xác nhận trước khi gọi `send`.

### 3. Team Eval Cases
Nhóm đã thêm thành công 10 cases (5 single-turn, 5 multi-turn) vào `data/eval_group.json`, bao gồm các cases khó về `multi-turn` thay đổi tool và thay đổi nội dung (carry over).

### 4. Live Chat Transcript
*(Sau khi chat trên giao diện Streamlit, copy một đoạn log thể hiện Agent hoạt động xuất sắc vào đây)*

```json
// Placeholder for transcript log showing successful Calculator or Confirm logic
```
