# Day 04 Lab v2 Report — Research Agent

## Phần A: Giới thiệu chung (Dùng cho Demo)

### 1. Agent Name & Mục tiêu
- **Tên Agent**: Wikipedia & Math Research Agent (Group 5)
- **Mục tiêu**: Hỗ trợ tìm kiếm thông tin, tra cứu tin tức, phân tích mạng xã hội, dự báo thời tiết, tính toán số học và tra cứu bách khoa toàn thư Wikipedia.

### 2. Các công cụ (Tools) nổi bật
- **Core Tools**: `clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `format`
- **Optional Tools**: `send`, `policy`, `papers`, `paper_text`
- **🔥 Các tool mới được thêm bởi nhóm**:
  - `calculator`: Thực hiện tính toán các biểu thức số học an toàn bằng Python `math` (được tối ưu hóa tự động chuyển đổi `^` sang `**` và hỗ trợ gọi hàm `math.xxx`).
  - `handle_lookup`: Tra cứu chính xác handle của người dùng từ tên hiển thị bằng danh mục nội bộ, hạn chế Agent tự đoán bừa.
  - `weather`: Xem dự báo thời tiết hiện tại của một địa điểm cụ thể.
  - `wiki_search` (Wikipedia Search): Công cụ tra cứu bách khoa toàn thư Wikipedia tiếng Anh qua API REST để lấy thông tin tóm tắt chuẩn xác của khái niệm, nhân vật hoặc sự kiện lịch sử.

### 3. Cách chạy Demo
```bash
# Bật Streamlit UI
streamlit run app.py
```
*(Nếu cần URL chia sẻ: `cloudflared tunnel --url http://localhost:8501`)*

### 4. Câu hỏi thử nghiệm tiêu biểu
- **Toán học & Công thức:** *"Tính giúp mình diện tích hình tròn có bán kính bằng 5"* -> Gọi `calculator` với biểu thức `math.pi * 5**2`.
- **Tra cứu Wikipedia:** *"Tra cứu Wikipedia về mạng neural nhân tạo (Artificial neural network)"* -> Gọi `wiki_search` với tiêu đề `Artificial neural network`.
- **Đăng bài & Xác nhận:** *"Đăng tin nhắn 'Hôm nay nghỉ họp nhé mọi người' lên group giúp mình"* -> Agent tự động gọi `clarify` loại `yes_no` để hỏi xác nhận trước khi dùng `send`.

---

## Phần B: Bằng chứng & Phân tích chi tiết

### 1. Version Log (Tóm tắt lịch sử cải tiến)

| Version | Tác giả | Changed Artifact | Artifact Version | Ý nghĩa cải tiến & Giả thuyết | Metric (Group Accuracy) | Run File |
| --- | --- | --- | --- | --- | --- | --- |
| `v0` | Team | none | v0+pba... | Chạy Baseline ban đầu. | 0.95 (Base) | `runs/v0_B_base_openrouter_20260729T152838925284.json` |
| `v1` | Team | system_prompt.md | v1+pba... | Sửa chỉ dẫn prompt bắt buộc gọi `clarify` khi thiếu URL/handle. | 0.95 (Base) | `runs/v1_B_base_openrouter_20260729T154451693743.json` |
| `v4` | Team | system_prompt.md | v4+p11... | Chặn model đoán handle Twitter không có trong danh sách map. | 1.00 (Group) | `runs/v4_B_group_openrouter_20260729T162255829087.json` |
| `v5` | Team | tools.yaml + handle_lookup | v5+pcf... | Thêm tool `handle_lookup` để tra cứu động thay vì hardcode. | 0.8182 (Group) | `runs/v5_B_group_openrouter_20260729T162545007995.json` |
| `v6` | Team | system_prompt.md + group json | v6+ped... | Khôi phục map inline đối với 3 tên nổi tiếng đã biết trước. | 1.00 (Group) | `runs/v6_B_group_openrouter_20260729T162803315913.json` |
| `v7` | Team | system_prompt.md | v7+p85... | Chặn model gọi handle_lookup thừa thãi đối với 3 tên inline. | 1.00 (Base) | `runs/v7_B_base_openrouter_20260729T163701426641.json` |
| `v8` | Team | tools.yaml + prompt + group | v8+p6b... | Thêm `weather` tool và các test case thời tiết (single & multi-turn). | 1.00 (Group) | `runs/v8_B_group_openrouter_20260729T165013390418.json` |
| `v9` | Team | tools.yaml + prompt + group | v9+p78... | Tích hợp `wiki_search` tool và sửa lỗi model tự đổi dấu cách thành `_`. | **1.00 (Group)** | `runs/v9_B_group_openrouter_20260729T165546800186.json` |

### 2. Failure Analysis & Bài học kinh nghiệm
- **Sự cố tự ý format biến (v9):** Khi tích hợp `wiki_search`, mô hình tự ý định dạng dấu cách thành dấu gạch dưới (VD: `Artificial_neural_network`), dẫn đến mismatch tham số mong đợi trong test case. 
- **Giải pháp:** Thay vì sửa đổi code logic của tool, chúng tôi cải tiến prompt hệ thống và tools.yaml để hướng dẫn mô hình giữ nguyên khoảng cách (spaces) của tiêu đề Wikipedia. Kết quả là tỷ lệ chính xác (accuracy) tăng từ `93.3%` lên `100%`.

### 3. Team Eval Cases
Nhóm đã mở rộng bộ đánh giá lên **15 test cases** trong file [eval_group.json](file:///d:/Aithucchien/K4_D304_Day04_Lab_A2/starter_v0/data/eval_group.json) bao gồm:
- Tính toán toán học phức tạp (`math.pi`, `math.sqrt`).
- Tra cứu thời tiết đơn lẻ và đa lượt.
- Hỏi xác nhận trước khi đăng bài và tiếp tục gửi sau khi xác nhận.
- Tra cứu tài khoản và đổi hướng quyết định của người dùng.
- Tra cứu Wikipedia (bao gồm cả case đổi ý ở lượt sau).

### 4. Live Chat Transcript mẫu (`wiki_search` & `calculator`)
Dưới đây là một phần log cuộc hội thoại thực tế của Agent chạy trên Streamlit UI:

```json
[
  {
    "role": "user",
    "content": "Tính giúp mình diện tích hình tròn có bán kính bằng 5"
  },
  {
    "role": "assistant",
    "content": "Diện tích hình tròn có bán kính bằng 5 là 78.53981633974483 đơn vị diện tích.",
    "tool_calls": [
      {
        "name": "calculator",
        "args": {
          "expression": "math.pi * 5**2"
        }
      }
    ],
    "tool_results": [
      {
        "tool": "calculator",
        "result": {
          "tool": "evaluate_expression",
          "expression": "math.pi * 5**2",
          "result": 78.53981633974483
        }
      }
    ]
  },
  {
    "role": "user",
    "content": "Tra cứu Wikipedia về mạng neural nhân tạo (Artificial neural network) xem sao"
  },
  {
    "role": "assistant",
    "content": "Mạng neural nhân tạo (Artificial Neural Network - ANN) là một mô hình tính toán trong học máy được lấy cảm hứng từ cấu trúc và chức năng của mạng neural sinh học.",
    "tool_calls": [
      {
        "name": "wiki_search",
        "args": {
          "title": "Artificial neural network"
        }
      }
    ],
    "tool_results": [
      {
        "tool": "wiki_search",
        "result": {
          "tool": "wiki_search",
          "title": "Artificial neural network",
          "summary": "In machine learning, a neural network (NN) or neural net, is a computational model inspired by the structure and functions of biological neural networks.",
          "url": "https://en.wikipedia.org/wiki/Neural_network_(machine_learning)"
        }
      }
    ]
  }
]
```
