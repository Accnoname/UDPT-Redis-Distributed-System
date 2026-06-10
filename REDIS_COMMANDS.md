# 📋 Sổ Tay Tra Cứu Lệnh Dự Án (Commands Reference)

Tài liệu này tổng hợp toàn bộ các câu lệnh cần thiết để vận hành, kiểm tra và bảo vệ dự án Hệ thống phân tán Redis trước thầy cô.

---

## 🐋 1. Nhóm Lệnh Docker (Quản lý các Container Redis)

| Nhiệm vụ | Câu lệnh |
|---|---|
| **Khởi động Redis đơn lẻ (Single Node)** | `docker-compose up -d` |
| **Tắt Redis đơn lẻ** | `docker-compose down` |
| **Khởi động Cụm Replication (1 Master + 2 Replicas)** | `docker-compose -f docker-compose-replica.yml up -d` |
| **Tắt Cụm Replication** | `docker-compose -f docker-compose-replica.yml down` |
| **Xem danh sách các container đang chạy** | `docker ps` |
| **Xem log của một container cụ thể** | `docker logs <tên_container>` (Ví dụ: `docker logs redis-master`) |

---

## 💻 2. Nhóm Lệnh Chạy Python Scripts (Demo dự án)

Trước khi chạy các script, hãy đảm bảo đã cài đặt thư viện bằng: `pip install -r requirements.txt`

| File / Tính năng | Lệnh khởi chạy | Lưu ý |
|---|---|---|
| **Day 1: Các lệnh cơ bản** | `python experiments/01_basics.py` | Cần chạy Redis Single hoặc Replication trước |
| **Day 2: Pub/Sub Subscriber** | `python experiments/02_pubsub_sub.py` | Chạy trước để lắng nghe |
| **Day 2: Pub/Sub Publisher** | `python experiments/02_pubsub_pub.py` | Chạy sau để gửi tin nhắn |
| **Day 2: Redis Streams Demo** | `python experiments/03_streams.py` | Chạy không đối số để tạo Job; thêm `worker-A` để xử lý |
| **Day 3: Replication Test** | `python experiments/04_replication.py` | **Bắt buộc** phải bật cụm Replication (port 6379, 6380, 6381) |
| **Feature 1: 3 Rate Limiter Servers** | `python feature1_rate_limiter/run_servers.py` | Mở trình duyệt tại: http://localhost:8001 |
| **Feature 2: Task Queue Dashboard** | `python feature2_task_queue/run_dashboard.py` | Mở trình duyệt tại: http://localhost:8002 |
| **Feature 2: Khởi động Worker** | `python feature2_task_queue/worker.py worker-A` | Có thể mở nhiều terminal để chạy thêm `worker-B`, `worker-C` |

---

## ⚡ 3. Nhóm Lệnh Redis CLI (Kiểm tra dữ liệu trực tiếp)

Để truy cập vào Redis CLI thông qua Docker container, chạy lệnh:
```bash
docker exec -it redis-master redis-cli
```

### 🔹 Các lệnh cơ bản (Key, String, Hash)
* **Kiểm tra ping:** `PING` $\rightarrow$ Trả về `PONG`
* **Tìm tất cả key:** `KEYS *`
* **Xem kiểu dữ liệu của key:** `TYPE <tên_key>` (Ví dụ: `TYPE task_stream`)
* **Xóa một key:** `DEL <tên_key>`
* **Xem dữ liệu Hash của Worker (Object):** `HGETALL worker:stats:worker-A`
* **Xem thời gian sống (TTL) còn lại của key:** `TTL <tên_key>` (Đơn vị: giây, `-1` là vô hạn)

### 🔹 Lệnh hàng đợi nâng cao (Redis Streams - Tính năng 2)
* **Đếm số lượng tác vụ trong Stream chính:**
  ```redis
  XLEN task_stream
  ```
* **Xem danh sách tác vụ bị lỗi trong Dead Letter Queue (DLQ):**
  ```redis
  XRANGE task_dlq - +
  ```
* **Kiểm tra danh sách các tác vụ đang bị treo (Pending) chưa được Worker gửi XACK:**
  ```redis
  XPENDING task_stream worker_group
  ```
* **Xem chi tiết nội dung của 5 tác vụ đầu tiên trong Stream chính:**
  ```redis
  XRANGE task_stream - + COUNT 5
  ```

---

## 🐙 4. Nhóm Lệnh Git (Đồng bộ mã nguồn lên GitHub)

| Nhiệm vụ | Câu lệnh |
|---|---|
| **Kiểm tra trạng thái các file thay đổi** | `git status` |
| **Thêm tất cả các file thay đổi vào hàng chờ** | `git add .` |
| **Tạo điểm lưu trữ (Commit) kèm tin nhắn** | `git commit -m "nội_dung_tin_nhắn"` |
| **Đẩy mã nguồn lên GitHub** | `git push origin main` |
| **Tải mã nguồn mới nhất từ GitHub về máy** | `git pull origin main` |
