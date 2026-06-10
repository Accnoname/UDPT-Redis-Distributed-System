# 🚀 Redis Distributed System Project

> Bài tập giữa kỳ môn Hệ Thống Phân Tán  
> Dự án: **Redis** — từ kho [awesome-distributed-system-projects](https://github.com/roma-glushko/awesome-distributed-system-projects)

## 📌 Giới Thiệu

Redis (Remote Dictionary Server) là một in-memory database mã nguồn mở, hỗ trợ đầy đủ các tính năng của hệ thống phân tán: replication, clustering, pub/sub, và streaming.

## 📁 Cấu Trúc Project

```
redis-project/
├── experiments/              # Thực nghiệm các tính năng Redis cơ bản
│   ├── 01_basics.py          # CRUD, data types
│   ├── 02_pubsub.py          # Publish/Subscribe
│   ├── 03_streams.py         # Redis Streams
│   └── 04_replication.py     # Replication test
├── feature1_rate_limiter/    # Tính năng 1: Distributed Rate Limiter
│   ├── rate_limiter.py       # Core logic
│   └── api_server.py         # FastAPI demo server
├── feature2_task_queue/      # Tính năng 2: Distributed Task Queue
│   ├── producer.py           # Gửi jobs vào queue
│   ├── worker.py             # Xử lý jobs
│   └── monitor.py            # Monitor real-time
├── docker-compose.yml        # Redis single instance
├── docker-compose-replica.yml # Redis replication
└── requirements.txt          # Python dependencies
```

## ⚙️ Cài Đặt

```bash
# 1. Cài Python dependencies
pip install -r requirements.txt

# 2. Chạy Redis bằng Docker
docker-compose up -d

# 3. Kiểm tra Redis đang chạy
docker ps
```

## 🧪 Thực Nghiệm

```bash
# Chạy từng experiment
python experiments/01_basics.py
python experiments/02_pubsub.py
python experiments/03_streams.py
```

## 🆕 Tính Năng Mới

### Feature 1: Distributed Rate Limiter
Giới hạn số request của user trên nhiều server đồng thời dùng Redis atomic counter.

### Feature 2: Distributed Task Queue
Hệ thống hàng đợi tác vụ với nhiều worker xử lý song song qua Redis Streams.

## 📚 Tài Liệu Tham Khảo

- [Redis Official Docs](https://redis.io/docs)
- [redis-py Documentation](https://redis-py.readthedocs.io)
- [awesome-distributed-system-projects](https://github.com/roma-glushko/awesome-distributed-system-projects)
