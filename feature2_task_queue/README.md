# Feature 2: Distributed Task Queue & Worker System (Hàng đợi tác vụ phân tán)

Hệ thống hàng đợi công việc phân tán sử dụng cấu trúc **Redis Streams** để phân phối tác vụ từ producer đến nhiều worker instances chạy độc lập song song.

## 💡 Thiết kế hệ thống
1. **At-Least-Once Delivery**: Sử dụng tính năng Consumer Group của Redis Streams (`xreadgroup`). Worker chỉ xác nhận đã xử lý thành công bằng lệnh `xack` sau khi hoàn thành tác vụ. Nếu worker bị crash giữa chừng, tác vụ sẽ nằm trong PEL (Pending Entries List) và có thể được xử lý lại, tránh mất mát dữ liệu.
2. **Dead Letter Queue (DLQ)**: Khi một job gặp lỗi xử lý quá 3 lần (được ghi nhận qua bộ đếm số lần retry trong Redis Hash `task:retries:<id>`), nó sẽ được tự động di chuyển sang hàng đợi cô lập (DLQ) `task_dlq` để tránh làm nghẽn hàng đợi chính.
3. **Worker Registry & Discovery**: Các worker định kỳ cập nhật trạng thái hoạt động (Idle/Processing) cùng tổng số job thành công/thất bại vào một Redis Hash (`worker:stats:<id>`) với thời gian hết hạn (TTL 60s). Dashboard có thể tự động quét và phát hiện các worker đang hoạt động trong thời gian thực.

## 🚀 Cách chạy thử nghiệm

1. Đảm bảo Docker (Redis Master) đang chạy.
2. Khởi động Dashboard UI Server:
   ```bash
   python feature2_task_queue/run_dashboard.py
   ```
3. Truy cập giao diện trực quan tại:
   👉 **[http://localhost:8002](http://localhost:8002)**
4. Khởi động các Workers để xử lý công việc từ hàng đợi (chạy trên các terminal khác nhau):
   - **Worker A**:
     ```bash
     python feature2_task_queue/worker.py worker-A
     ```
   - **Worker B**:
     ```bash
     python feature2_task_queue/worker.py worker-B
     ```
   - **Worker C**:
     ```bash
     python feature2_task_queue/worker.py worker-C
     ```
5. Click **"Tạo nhanh 10 Tasks ngẫu nhiên"** trên giao diện để theo dõi khả năng chia tải và xử lý lỗi thời gian thực giữa các Workers!
