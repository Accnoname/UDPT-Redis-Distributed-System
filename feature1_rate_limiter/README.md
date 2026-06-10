# Feature 1: Distributed Rate Limiter (Bộ giới hạn tốc độ phân tán)

Hệ thống giới hạn tốc độ phân tán sử dụng Redis làm cơ sở dữ liệu dùng chung để đồng bộ hóa trạng thái request trên nhiều server instance (chạy trên các port 8001, 8002, 8003).

## 💡 Thuật toán: Sliding Window Log (ZSET)
Rate Limiter sử dụng cấu trúc dữ liệu **Sorted Set (ZSET)** của Redis để lưu trữ timestamp của các request. Mỗi khi có request mới:
1. Xóa các request cũ nằm ngoài khung thời gian trượt (Window size).
2. Đếm số request hiện tại còn lại trong ZSET.
3. Nếu chưa vượt quá giới hạn (Limit) → Thêm request mới vào ZSET và cho phép đi tiếp.
4. Nếu vượt quá → Từ chối và trả về lỗi 429.

**Đặc biệt:** Toàn bộ thuật toán được đóng gói thành một **Lua script** chạy trực tiếp trên Redis Engine để đảm bảo tính **Atomic (nguyên tử)**, tránh hoàn toàn lỗi Race Condition khi có hàng nghìn server cùng ghi vào.

## 🚀 Cách chạy thử nghiệm

1. Đảm bảo Docker (Redis Master) đang chạy.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install fastapi uvicorn redis
   ```
3. Chạy script để khởi động cùng lúc 3 FastAPI servers:
   ```bash
   python feature1_rate_limiter/run_servers.py
   ```
4. Truy cập giao diện trực quan tại:
   👉 **[http://localhost:8001](http://localhost:8001)**
