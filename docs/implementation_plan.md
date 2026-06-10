# 📚 Kế Hoạch Bài Tập Giữa Kỳ — Hệ Thống Phân Tán

## 🎯 Mục Tiêu

Chọn 1 dự án từ kho `awesome-distributed-system-projects`, cài đặt, thực nghiệm, phát triển **2 tính năng mới liên quan đến xử lý phân tán**, rồi viết báo cáo & slides.

---

## ✅ Đề Xuất Dự Án: **`toydb`** (Rust) → Thay thế bằng **`immudb`** (Go) → **Gợi ý tốt nhất cho Python: `Celery` + `Redis` pattern**

> [!IMPORTANT]
> Vì nhóm quen **Python**, tôi đề xuất dự án **`oklog`** hoặc **xây dựng lại dựa trên `redis`** — đây là 2 hướng khả thi nhất. Xem phân tích bên dưới.

---

## 🔍 Phân Tích Các Dự Án Phù Hợp

### So sánh các lựa chọn

| Dự Án | Ngôn ngữ gốc | Độ khó | Python-friendly | Điểm số tiềm năng |
|-------|-------------|--------|-----------------|-------------------|
| **redis** | C | ⭐⭐ | ✅ Rất tốt (có Python client) | 8-9/10 |
| **Jocko** (Kafka-like) | Go | ⭐⭐⭐ | ⚠️ Trung bình | 7-8/10 |
| **toydb** | Rust | ⭐⭐⭐⭐ | ❌ Khó | 6-7/10 |
| **oklog** | Go | ⭐⭐ | ⚠️ Trung bình | 7/10 |
| **immudb** | Go | ⭐⭐⭐ | ✅ Có REST API | 7-8/10 |

---

## 🏆 Dự Án Được Chọn: `redis` (In-memory Distributed Database)

### Lý Do Chọn Redis

1. **Cực kỳ phổ biến** — dễ trình bày, giáo viên quen
2. **Python-friendly** — thư viện `redis-py` đầy đủ
3. **Phong phú về tính năng phân tán**: clustering, replication, pub/sub
4. **Tài liệu tốt** — dễ cài đặt và demo
5. **2 tính năng mới rất khả thi** bằng Python

---

## 📋 Kế Hoạch Chi Tiết

### Phase 1: Cài Đặt & Thực Nghiệm (2-3 ngày)

#### 1.1 Cài Redis với Docker Cluster
```bash
# Redis Cluster 3 master + 3 replica
docker-compose up -d
```

#### 1.2 Kết Nối Python
```python
pip install redis hiredis
```

#### 1.3 Thực Nghiệm Cơ Bản
- CRUD operations
- Pub/Sub messaging
- Redis Streams
- Redis Cluster (sharding)
- Replication (master-slave)

---

### Phase 2: Tính Năng Mới (3-4 ngày)

#### 🆕 Tính Năng 1: **Distributed Rate Limiter** (Giới hạn tốc độ phân tán)

**Mô tả:** Xây dựng hệ thống rate limiting phân tán dùng Redis để giới hạn số request của mỗi user/IP trên nhiều server cùng lúc.

**Tại sao liên quan đến phân tán:**
- Nhiều server xử lý request cùng lúc, cần đồng bộ counter qua Redis
- Dùng Redis Lua scripts (atomic operations) để tránh race condition
- Có thể scale horizontally

**Stack:** Python (FastAPI) + Redis

```python
# Minh họa ý tưởng
def is_rate_limited(user_id: str, limit: int = 100, window: int = 60) -> bool:
    key = f"rate:{user_id}:{window_slot}"
    current = redis.incr(key)
    if current == 1:
        redis.expire(key, window)
    return current > limit
```

**Điểm demo:** Chạy 3 FastAPI server cùng lúc, rate limit được chia sẻ qua Redis

---

#### 🆕 Tính Năng 2: **Distributed Task Queue & Worker System** (Hàng đợi tác vụ phân tán)

**Mô tả:** Xây dựng hệ thống hàng đợi tác vụ phân tán — producer gửi job vào Redis Queue, nhiều worker Node độc lập xử lý song song.

**Tại sao liên quan đến phân tán:**
- Work distribution across multiple nodes
- At-least-once delivery guarantee
- Dead letter queue cho failed tasks
- Worker discovery & health monitoring

**Stack:** Python + Redis Streams (XADD/XREADGROUP)

```python
# Producer
redis.xadd("task_queue", {"job": "process_image", "file": "img.jpg"})

# Worker (nhiều instance chạy song song)
messages = redis.xreadgroup("workers", "worker-1", {"task_queue": ">"})
```

**Điểm demo:** Chạy 1 producer + 3 worker, thấy load được phân chia

---

### Phase 3: Báo Cáo & Slides (2-3 ngày)

#### Cấu Trúc Báo Cáo (≤20 trang)

| # | Nội Dung | Trang |
|---|---------|-------|
| 1 | Bìa + Mục lục | 1-2 |
| 2 | Dự án Redis: Giới thiệu | 2-3 |
| 3 | Mục đích, chức năng, ứng dụng thực tế | 3-4 |
| 4 | Kiến trúc phân tán của Redis | 4-5 |
| 5 | Cài đặt + Kết quả thực nghiệm | 5-8 |
| 6 | Tính năng mới 1: Distributed Rate Limiter | 8-12 |
| 7 | Tính năng mới 2: Distributed Task Queue | 12-16 |
| 8 | Kết quả benchmark / demo | 16-18 |
| 9 | Đóng góp từng thành viên | 18-19 |
| 10 | Tài liệu tham khảo | 20 |

---

## 📅 Timeline

| Tuần | Việc Cần Làm |
|------|-------------|
| **Tuần 1** (đã qua 29/5) | Setup GitHub repo, cài Redis, commit cơ bản |
| **Tuần 2** | Thực nghiệm Redis features, document kết quả |
| **Tuần 3** | Code tính năng 1: Distributed Rate Limiter |
| **Tuần 4** | Code tính năng 2: Distributed Task Queue |
| **Tuần 5** | Viết báo cáo + Tạo slides |
| **Tuần 6** | Review, fix bugs, chuẩn bị trình bày |

---

## 🗂️ Cấu Trúc GitHub Repository

```
your-repo/
├── README.md               # Mô tả dự án
├── docker-compose.yml      # Redis cluster setup
├── experiments/            # Thực nghiệm cơ bản
│   ├── 01_basic_crud.py
│   ├── 02_pubsub.py
│   ├── 03_replication_test.py
│   └── 04_cluster_test.py
├── feature1_rate_limiter/  # Tính năng 1
│   ├── README.md
│   ├── rate_limiter.py
│   ├── api_server.py
│   └── tests/
├── feature2_task_queue/    # Tính năng 2
│   ├── README.md
│   ├── producer.py
│   ├── worker.py
│   ├── monitor.py
│   └── tests/
├── report/                 # Báo cáo
│   └── midterm_report.pdf
└── slides/                 # Slides
    └── presentation.pdf
```

---

## 💡 Tips Để Đạt Điểm Cao

> [!TIP]
> **Commit thường xuyên** từ ngày 29/5 — giáo viên sẽ xem lịch sử commit. Mỗi ngày nên có ít nhất 1 commit có ý nghĩa.

> [!IMPORTANT]
> **Demo trực quan** trong 10 phút: Chuẩn bị sẵn terminal chạy cluster, visualize real-time với dashboard đơn giản.

> [!TIP]
> **Điểm hỏi đáp**: Cần nắm vững: CAP theorem, Consistency vs Availability, Redis Sentinel vs Cluster, RESP protocol.

---

## ❓ Câu Hỏi Mở (Cần Nhóm Xác Nhận)

1. Nhóm bạn có **bao nhiêu thành viên**? (để phân công đóng góp)
2. Deadline cụ thể là **ngày nào** để tôi giúp lên timeline chính xác?
3. Bạn có muốn tôi **tạo luôn code** cho 2 tính năng mới không?
4. Cần tôi tạo **báo cáo LaTeX** hay Word format?
