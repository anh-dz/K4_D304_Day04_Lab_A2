---
name: calculator
description: "Thực hiện tính toán biểu thức toán học."
---

# Calculator Tool

Dùng tool này khi người dùng yêu cầu tính toán một phép toán. Truyền biểu thức toán học vào dưới dạng chuỗi (ví dụ: `2 + 2 * 3` hoặc `math.sqrt(16)`). Không dùng cho các câu hỏi logic hay phương trình phức tạp nằm ngoài khả năng của hàm eval cơ bản.

## Khi nào dùng
- Khi người dùng hỏi kết quả của phép toán cơ bản hoặc hàm trong thư viện `math`.
- Ví dụ: "15% của 200 là bao nhiêu?", "tính sin(pi/4)".

## Argument
- `expression`: Chuỗi chứa biểu thức cần tính.
