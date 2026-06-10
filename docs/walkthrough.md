# 🚀 Lộ Trình 4 Ngày Hiểu Redis & Hệ Thống Phân Tán

> **Mục tiêu:** Sau 4 ngày, bạn hiểu Redis là gì, nó giải quyết vấn đề phân tán như thế nào,
> và có thể tự cài đặt + demo thuyết phục được giáo viên.

---

## 🧠 BIG PICTURE: Redis Là Gì Trong Hệ Thống Phân Tán?

```
Vấn đề thực tế:
  App Server 1 ──┐
  App Server 2 ──┼──► Cần chia sẻ dữ liệu ◄── Đây là bài toán phân tán!
  App Server 3 ──┘

Giải pháp Redis:
  App Server 1 ──┐
  App Server 2 ──┼──► Redis (shared memory) ──► Mọi server đều thấy cùng data
  App Server 3 ──┘
```

**Redis = Remote Dictionary Server**
- Lưu dữ liệu **in-memory** (trong RAM) → cực nhanh
- Hỗ trợ **nhiều kiểu dữ liệu**: String, List, Hash, Set, Sorted Set, Stream...
- Có thể **replicate** (sao chép) và **cluster** (phân tán) → đây là phần phân tán!
- Được dùng bởi: Twitter, GitHub, Instagram, Stack Overflow

---

## 📅 NGÀY 1: Nền Tảng — "Tại Sao Cần Hệ Thống Phân Tán?"

### 🎯 Mục Tiêu Ngày 1
- Hiểu vấn đề mà Redis giải quyết
- Cài Redis và chạy thử lệnh cơ bản
- Hiểu các kiểu dữ liệu Redis

---

### 📖 Lý Thuyết (1-2 giờ)

#### Bài Toán Cốt Lõi: Scalability

```
Scenario 1: Một server duy nhất
┌─────────────┐
│   App + DB  │ ← Tất cả trên 1 máy
└─────────────┘
✅ Đơn giản
❌ Nếu máy chết → toàn bộ hệ thống chết
❌ Không thể xử lý triệu user

Scenario 2: Nhiều server, không có shared state
┌─────────┐  ┌─────────┐  ┌─────────┐
│  App 1  │  │  App 2  │  │  App 3  │
│  DB 1   │  │  DB 2   │  │  DB 3   │
└─────────┘  └─────────┘  └─────────┘
❌ User login App 1, chuyển sang App 2 → mất session!
❌ Counter trên App 1 không biết App 2 đếm bao nhiêu

Scenario 3: Nhiều server + Redis
┌─────────┐  ┌─────────┐  ┌─────────┐
│  App 1  │  │  App 2  │  │  App 3  │
└────┬────┘  └────┬────┘  └────┬────┘
     └────────────┴────────────┘
                  │
             ┌────▼────┐
             │  Redis  │  ← Shared State!
             └─────────┘
✅ Tất cả server thấy cùng data
✅ Session được chia sẻ
✅ Counter đồng bộ
```

#### CAP Theorem — Định Lý Nền Tảng Của Hệ Thống Phân Tán

```
        Consistency (Nhất quán)
              /\
             /  \
            /    \
           /      \
          /________\
  Availability    Partition Tolerance
  (Sẵn sàng)     (Chịu lỗi mạng)

❗ Không hệ thống nào có thể đạt cả 3 cùng lúc!
   Phải chọn 2 trong 3.

Redis chọn: CP (Consistency + Partition Tolerance)
→ Khi mạng bị phân tách, Redis ưu tiên nhất quán dữ liệu
→ Có thể từ chối write nếu không đủ quorum
```

#### Tại Sao Redis Là Dự Án "Hệ Thống Phân Tán"?

| Tính Năng | Khái Niệm Phân Tán |
|-----------|-------------------|
| Replication | Sao chép dữ liệu sang nhiều node |
| Redis Cluster | Sharding — phân mảnh dữ liệu ra nhiều máy |
| Pub/Sub | Message passing giữa các tiến trình |
| Redis Streams | Distributed event streaming |
| Redis Sentinel | Automatic failover — tự phục hồi khi node chết |

---

### 💻 Thực Hành Ngày 1 (2-3 giờ)

#### Bước 1: Cài Redis bằng Docker
```bash
# Cài Docker Desktop trước nếu chưa có
# https://www.docker.com/products/docker-desktop/

# Chạy Redis đơn giản
docker run -d --name redis-single -p 6379:6379 redis:7.2

# Kiểm tra Redis đang chạy
docker ps

# Vào Redis CLI
docker exec -it redis-single redis-cli
```

#### Bước 2: Thử Các Lệnh Cơ Bản trong Redis CLI
```redis
# STRING - Kiểu dữ liệu cơ bản nhất
SET name "Nguyen Van A"
GET name
SET counter 0
INCR counter          # Tăng 1 (atomic!)
INCR counter
GET counter           # → "2"
INCRBY counter 10     # Tăng 10
TTL name              # Xem thời gian sống (-1 = không hết hạn)
EXPIRE name 60        # Set hết hạn sau 60 giây

# LIST - Hàng đợi
RPUSH tasks "task1" "task2" "task3"
LRANGE tasks 0 -1     # Xem toàn bộ list
LPOP tasks            # Lấy phần tử đầu (như queue)
RPUSH tasks "task4"
LLEN tasks            # Độ dài list

# HASH - Lưu object
HSET user:1 name "An" age 22 email "an@email.com"
HGET user:1 name
HGETALL user:1        # Lấy toàn bộ fields
HSET user:1 age 23    # Cập nhật field

# SET - Tập hợp không trùng lặp
SADD online_users "user1" "user2" "user3"
SADD online_users "user1"  # Không thêm vào (đã có)
SMEMBERS online_users
SCARD online_users    # Đếm số phần tử
SISMEMBER online_users "user1"  # Check xem có trong set không

# SORTED SET - Xếp hạng (leaderboard)
ZADD leaderboard 1500 "player1"
ZADD leaderboard 2300 "player2"
ZADD leaderboard 800  "player3"
ZRANGE leaderboard 0 -1 WITHSCORES REV  # Top players
ZRANK leaderboard "player1"  # Xếp hạng của player1
```

#### Bước 3: Kết Nối Python
```bash
pip install redis
```

```python
# file: day1_basics.py
import redis

# Kết nối
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Test kết nối
print("Ping:", r.ping())  # True

# String operations
r.set("greeting", "Hello from Python!")
print(r.get("greeting"))

# Counter (distributed-safe với INCR)
r.set("page_views", 0)
for i in range(5):
    views = r.incr("page_views")
    print(f"Views: {views}")

# Hash - lưu user info
r.hset("user:1001", mapping={
    "name": "Nguyen Van A",
    "email": "a@example.com", 
    "score": 0
})
print(r.hgetall("user:1001"))

# List - Task queue simulation
tasks = ["send_email", "resize_image", "generate_report"]
for task in tasks:
    r.rpush("task_queue", task)

# Worker nhận task
while r.llen("task_queue") > 0:
    task = r.lpop("task_queue")
    print(f"Processing: {task}")
```

---

### 🧪 Câu Hỏi Ôn Tập Ngày 1

1. INCR trong Redis có phải là atomic operation không? Tại sao điều đó quan trọng trong hệ thống phân tán?
2. Sự khác biệt giữa LIST và SET trong Redis là gì?
3. CAP theorem nói gì? Redis thuộc nhóm nào (CP, AP, hay CA)?
4. Tại sao dùng Redis để lưu session thay vì lưu trong memory của từng server?

---

## 📅 NGÀY 2: Pub/Sub & Streams — Giao Tiếp Phân Tán

### 🎯 Mục Tiêu Ngày 2
- Hiểu Pub/Sub pattern (publish-subscribe)
- Hiểu Redis Streams — cơ chế event streaming mạnh mẽ
- Thực hành giao tiếp giữa nhiều tiến trình Python

---

### 📖 Lý Thuyết (1-2 giờ)

#### Pub/Sub: Giao Tiếp Không Đồng Bộ

```
Không dùng Pub/Sub (tightly coupled):
  Service A ──► gọi trực tiếp ──► Service B
  ❌ A phải biết B tồn tại
  ❌ Nếu B chết, A bị lỗi

Dùng Pub/Sub (loosely coupled):
  Service A (Publisher) ──► Redis Channel ──► Service B (Subscriber)
                                          ──► Service C (Subscriber)
                                          ──► Service D (Subscriber)
  ✅ A không cần biết B, C, D tồn tại
  ✅ Thêm subscriber mới không ảnh hưởng A
  ✅ Loosely coupled architecture
```

**Hạn chế của Pub/Sub:**
- Message bị mất nếu subscriber chưa kết nối
- Không có lưu trữ lịch sử
- → Giải pháp: **Redis Streams**

#### Redis Streams: Event Log Phân Tán

```
Redis Streams = Kafka đơn giản hơn

Producer ──► [event1, event2, event3, ...] ──► Consumer Group
                                                  ├── Worker 1
                                                  ├── Worker 2
                                                  └── Worker 3

Ưu điểm:
✅ Message được lưu trữ (không mất)
✅ Consumer group — nhiều worker chia nhau xử lý
✅ Acknowledge — biết message đã được xử lý
✅ Replay — đọc lại lịch sử
```

---

### 💻 Thực Hành Ngày 2 (3-4 giờ)

#### Bài Tập 1: Pub/Sub Chat Đơn Giản
```python
# file: day2_pubsub_publisher.py
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("Publisher started. Sending messages...")
channels = ["news", "sports", "tech"]

for i in range(10):
    import random
    channel = random.choice(channels)
    message = f"Message #{i} on {channel}: {time.time()}"
    
    subscribers = r.publish(channel, message)
    print(f"Published to '{channel}': {message} ({subscribers} subscribers)")
    time.sleep(1)
```

```python
# file: day2_pubsub_subscriber.py  (chạy TRƯỚC publisher)
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
pubsub = r.pubsub()

# Subscribe nhiều channels
pubsub.subscribe("news", "tech")
print("Subscriber listening on: news, tech")

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"[{message['channel']}] {message['data']}")
```

```bash
# Mở 2 terminal, chạy:
# Terminal 1: python day2_pubsub_subscriber.py
# Terminal 2: python day2_pubsub_publisher.py
```

#### Bài Tập 2: Redis Streams — Distributed Job Queue

```python
# file: day2_streams_producer.py
import redis
import time
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Tạo consumer group (chỉ cần làm 1 lần)
try:
    r.xgroup_create("jobs", "workers", id="0", mkstream=True)
    print("Consumer group created")
except redis.exceptions.ResponseError:
    print("Consumer group already exists")

job_types = ["resize_image", "send_email", "generate_report", "process_payment"]

print("Producer: Sending jobs...")
for i in range(20):
    job = {
        "id": f"job-{i:03d}",
        "type": random.choice(job_types),
        "priority": random.randint(1, 5),
        "created_at": str(time.time())
    }
    msg_id = r.xadd("jobs", job)
    print(f"Added job: {job['id']} ({job['type']}) → ID: {msg_id}")
    time.sleep(0.2)

print("Producer done!")
```

```python
# file: day2_streams_worker.py  (chạy nhiều instance cùng lúc!)
import redis
import time
import sys

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker-1"
print(f"[{worker_id}] Starting...")

processed = 0
while True:
    # Lấy job từ stream (blocking 2 giây)
    messages = r.xreadgroup(
        groupname="workers",
        consumername=worker_id,
        streams={"jobs": ">"},  # ">" = chỉ lấy chưa deliver
        count=1,
        block=2000
    )
    
    if not messages:
        print(f"[{worker_id}] No more jobs. Processed: {processed}")
        break
    
    for stream_name, msg_list in messages:
        for msg_id, job in msg_list:
            print(f"[{worker_id}] Processing: {job['id']} ({job['type']})")
            
            # Giả lập xử lý
            processing_time = random.uniform(0.5, 2.0)
            time.sleep(processing_time)
            
            # Acknowledge — báo đã xử lý xong
            r.xack("jobs", "workers", msg_id)
            processed += 1
            print(f"[{worker_id}] Done: {job['id']} (took {processing_time:.1f}s)")

import random
```

```bash
# Mở 4 terminal:
# Terminal 1: python day2_streams_producer.py
# Terminal 2: python day2_streams_worker.py worker-1
# Terminal 3: python day2_streams_worker.py worker-2
# Terminal 4: python day2_streams_worker.py worker-3
# Quan sát cách jobs được phân chia cho các worker!
```

---

### 🧪 Câu Hỏi Ôn Tập Ngày 2

1. Sự khác biệt giữa Pub/Sub và Redis Streams là gì?
2. Consumer Group trong Redis Streams giải quyết vấn đề gì?
3. Tại sao cần XACK sau khi xử lý xong message?
4. Điều gì xảy ra với message nếu worker bị crash trước khi XACK?

---

## 📅 NGÀY 3: Replication & Clustering — Phân Tán Thực Sự

### 🎯 Mục Tiêu Ngày 3
- Hiểu Redis Replication (Master-Slave)
- Cài Redis Cluster với Docker
- Hiểu cách sharding hoạt động
- Test failover scenario

---

### 📖 Lý Thuyết (1-2 giờ)

#### Redis Replication

```
Master-Replica Architecture:

  ┌──────────────┐
  │    Master    │ ← Nhận tất cả WRITE operations
  │  (Primary)   │
  └──────┬───────┘
         │  Replication (async)
    ┌────┴────────────────┐
    │                     │
┌───▼────┐          ┌─────▼───┐
│Replica1│          │Replica2 │  ← Chỉ READ, không ghi
└────────┘          └─────────┘

Ưu điểm:
✅ Read scalability — nhiều Replica phục vụ READ
✅ Data redundancy — dữ liệu có nhiều bản sao
✅ Failover — nếu Master chết, Replica lên thay

Nhược điểm:
❌ Replication lag — Replica có thể lag sau Master
❌ Write bottleneck — tất cả write vẫn vào 1 Master
```

#### Redis Cluster — Sharding

```
Vấn đề: 1 Master không đủ cho hàng TB data

Giải pháp: Chia data thành 16384 hash slots

  ┌─────────────────────────────────────┐
  │              Redis Cluster           │
  │                                     │
  │  Master1        Master2      Master3 │
  │  slots 0-5460   5461-10922   10923-  │
  │      │              │        16383   │
  │  Replica1       Replica2   Replica3  │
  └─────────────────────────────────────┘

Khi client muốn SET key "username":
  1. Tính HASH_SLOT = CRC16("username") % 16384 = 5649
  2. Slot 5649 thuộc Master2 → gửi request đến Master2
  3. Hoặc nhận MOVED redirect nếu kết nối sai node

✅ Horizontal scaling — thêm node = thêm capacity
✅ No single point of failure
✅ Tự động rebalance khi thêm/xóa node
```

---

### 💻 Thực Hành Ngày 3 (3-4 giờ)

#### Bước 1: Setup Redis Replication với Docker
```yaml
# file: docker-compose-replication.yml
version: '3.8'
services:
  redis-master:
    image: redis:7.2
    container_name: redis-master
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    
  redis-replica-1:
    image: redis:7.2
    container_name: redis-replica-1
    ports:
      - "6380:6379"
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master
      
  redis-replica-2:
    image: redis:7.2
    container_name: redis-replica-2
    ports:
      - "6381:6379"
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master
```

```bash
docker-compose -f docker-compose-replication.yml up -d

# Kiểm tra replication info
docker exec redis-master redis-cli INFO replication
```

#### Bước 2: Test Replication với Python
```python
# file: day3_replication_test.py
import redis
import time

# Kết nối master và replicas
master = redis.Redis(host='localhost', port=6379, decode_responses=True)
replica1 = redis.Redis(host='localhost', port=6380, decode_responses=True)
replica2 = redis.Redis(host='localhost', port=6381, decode_responses=True)

print("=== Redis Replication Demo ===\n")

# Write vào Master
print("1. Writing to Master...")
for i in range(5):
    master.set(f"key:{i}", f"value-{i}")
    master.hset(f"user:{i}", mapping={"name": f"User{i}", "score": i*100})

print("   Wrote 5 keys to master\n")
time.sleep(0.1)  # Đợi replication

# Đọc từ Replicas
print("2. Reading from Replica 1:")
for i in range(5):
    val = replica1.get(f"key:{i}")
    print(f"   key:{i} = {val}")

print("\n3. Reading from Replica 2:")
for i in range(5):
    val = replica2.get(f"key:{i}")
    print(f"   key:{i} = {val}")

# Kiểm tra replication info
print("\n4. Replication Status:")
info = master.info('replication')
print(f"   Role: {info['role']}")
print(f"   Connected Replicas: {info['connected_slaves']}")

# Thử write vào Replica (sẽ bị từ chối)
print("\n5. Trying to write to Replica (should fail):")
try:
    replica1.set("test", "value")
    print("   Unexpected: Write succeeded!")
except redis.exceptions.ReadOnlyError as e:
    print(f"   Expected error: {e}")
    print("   Replicas are READ-ONLY by design!")
```

#### Bước 3: Setup Redis Cluster
```yaml
# file: docker-compose-cluster.yml
version: '3.8'
services:
  redis-node-1:
    image: redis:7.2
    container_name: redis-node-1
    ports:
      - "7001:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes.conf
      --cluster-node-timeout 5000
      --appendonly yes

  redis-node-2:
    image: redis:7.2
    container_name: redis-node-2
    ports:
      - "7002:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes.conf
      --cluster-node-timeout 5000
      --appendonly yes

  redis-node-3:
    image: redis:7.2
    container_name: redis-node-3
    ports:
      - "7003:6379"
    command: >
      redis-server
      --cluster-enabled yes
      --cluster-config-file nodes.conf
      --cluster-node-timeout 5000
      --appendonly yes
```

```bash
docker-compose -f docker-compose-cluster.yml up -d

# Lấy IP của các node
docker inspect redis-node-1 | grep IPAddress
docker inspect redis-node-2 | grep IPAddress
docker inspect redis-node-3 | grep IPAddress

# Tạo cluster (thay IP thực tế)
docker exec -it redis-node-1 redis-cli --cluster create \
  172.20.0.2:6379 172.20.0.3:6379 172.20.0.4:6379 \
  --cluster-replicas 0 --cluster-yes
```

```python
# file: day3_cluster_test.py
from redis.cluster import RedisCluster

# Kết nối cluster
rc = RedisCluster(
    host="localhost", port=7001,
    decode_responses=True,
    skip_full_coverage_check=True
)

print("=== Redis Cluster Demo ===\n")

# Test sharding — xem key nằm ở node nào
keys_to_test = ["user:1", "session:abc", "counter:page", "product:42", "order:999"]
for key in keys_to_test:
    rc.set(key, f"value_for_{key}")
    node = rc.get_node_from_key(key)
    print(f"Key '{key}' → Node {node.host}:{node.port}")

# Cluster info
print("\nCluster Info:")
info = rc.cluster_info()
print(f"  State: {info['cluster_state']}")
print(f"  Nodes: {info['cluster_known_nodes']}")
print(f"  Slots assigned: {info['cluster_slots_assigned']}")
```

---

### 🧪 Câu Hỏi Ôn Tập Ngày 3

1. Sự khác biệt giữa Replication và Clustering trong Redis là gì?
2. Hash slot là gì? Tại sao Redis dùng 16384 slots?
3. Điều gì xảy ra khi Master trong cluster bị chết?
4. Tại sao Replica là READ-ONLY?

---

## 📅 NGÀY 4: Tổng Hợp — Chuẩn Bị Cho Tính Năng Mới

### 🎯 Mục Tiêu Ngày 4
- Ôn lại toàn bộ, viết code clean
- Hiểu rõ 2 tính năng sẽ phát triển
- Setup GitHub repo chuẩn
- Commit lịch sử học tập

---

### 📖 Tổng Kết Kiến Thức

#### Bản Đồ Kiến Thức Redis

```
                    REDIS
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   Data Types    Distributed    Persistence
        │          Features          │
   ┌────┴────┐        │          ┌───┴───┐
   String    │   ┌────┴────┐     RDB    AOF
   List      │   Replicate  │
   Hash      │   Cluster    │
   Set       │   Pub/Sub    │
   ZSet      │   Streams    │
   Stream    │   Sentinel   │
```

#### Các Lệnh Quan Trọng Cần Thuộc
```redis
# Monitoring
INFO all              # Toàn bộ thông tin Redis
INFO replication      # Trạng thái replication
INFO memory           # Sử dụng memory
DBSIZE                # Số keys
MONITOR               # Real-time command log (debug)
SLOWLOG GET 10        # 10 lệnh chậm nhất

# Atomic operations (quan trọng cho distributed!)
INCR / INCRBY         # Tăng counter atomic
SETNX key value       # Set if Not eXists
SET key value NX EX 60  # Set + conditional + TTL
GETSET key new_value  # Get old, set new (atomic)

# Transactions
MULTI                 # Bắt đầu transaction
SET key1 val1
SET key2 val2
EXEC                  # Thực thi tất cả

# Lua scripts (guaranteed atomic)
EVAL "return redis.call('INCR', KEYS[1])" 1 mykey
```

---

### 💻 Thực Hành Ngày 4: Setup GitHub Repo

```bash
# 1. Tạo repo local
mkdir redis-distributed-project
cd redis-distributed-project
git init

# 2. Tạo structure
mkdir -p experiments feature1_rate_limiter feature2_task_queue docs

# 3. Tạo README
echo "# Redis Distributed System Project" > README.md

# 4. Commit ngay!
git add .
git commit -m "feat: initial project structure"

# 5. Push lên GitHub
git remote add origin https://github.com/YOUR_USERNAME/redis-distributed-project.git
git push -u origin main
```

#### Sơ Đồ Kế Hoạch 2 Tính Năng Mới

```
Tính Năng 1: Distributed Rate Limiter
─────────────────────────────────────
User Request → FastAPI Server 1 ─┐
User Request → FastAPI Server 2 ─┼─► Redis ──► Check rate limit
User Request → FastAPI Server 3 ─┘            (shared counter)
                                                     │
                                              Allow / Deny

Tính Năng 2: Distributed Task Queue
─────────────────────────────────────
Job Creator → Redis Stream ──► Worker Pool
                               ├── Worker 1 (process job A)
                               ├── Worker 2 (process job B)
                               └── Worker 3 (process job C)
                               
                               Dead Letter Queue (failed jobs)
                               Monitor Dashboard (real-time stats)
```

---

### 📋 Checklist Trước Khi Code Tính Năng Mới

- [ ] Đã hiểu Redis data types (String, List, Hash, Set, Stream)
- [ ] Đã chạy được Pub/Sub với 2 terminal
- [ ] Đã chạy được Streams với producer + 2 workers
- [ ] Đã setup được Replication (master + 2 replicas)
- [ ] Đã hiểu CAP theorem và vị trí Redis trong đó
- [ ] Đã tạo GitHub repo và commit ít nhất 5 lần
- [ ] Có thể giải thích: "Tại sao INCR là atomic trong Redis?"
- [ ] Có thể giải thích: "Sự khác biệt giữa Replication và Clustering?"

---

## 📚 Tài Liệu Tham Khảo

| Tài Liệu | Link | Mức Độ |
|---------|------|--------|
| Redis Official Docs | https://redis.io/docs | ⭐⭐⭐ Bắt buộc |
| Redis University (free) | https://university.redis.com | ⭐⭐ Nên xem |
| Redis Streams Intro | https://redis.io/docs/data-types/streams | ⭐⭐⭐ Ngày 2 |
| Redis Cluster Tutorial | https://redis.io/docs/management/scaling | ⭐⭐⭐ Ngày 3 |
| redis-py docs | https://redis-py.readthedocs.io | ⭐⭐⭐ Cần đọc |

---

## ⏱️ Tóm Tắt Timeline (Đã Hoàn Thành)

| Ngày | Sáng (2-3h) | Chiều (2-3h) | Trạng Thái | Commit |
|------|------------|-------------|------------|--------|
| **Day 1** | Lý thuyết CAP, cài Redis | CRUD + Python basics | ✅ Xong | `feat: day1 basics experiments` |
| **Day 2** | Pub/Sub theory | Streams + multi-worker | ✅ Xong | `feat: day2 pubsub and streams` |
| **Day 3** | Replication theory | Cài đặt & Test Replication | ✅ Xong | `feat: day3 replication and cluster` |
| **Day 4** | Thiết kế 2 tính năng mới | Code Feature 1 & Feature 2 | ✅ Xong | `feat: implement distributed rate limiter...` |
| **Day 5** | Kiểm thử & Đẩy lên GitHub | Hoàn tất báo cáo | ✅ Xong | `git push origin main` |

---

## 🚀 CHI TIẾT 2 TÍNH NĂNG MỚI ĐÃ HOÀN THÀNH

### 🛡️ Feature 1: Distributed Rate Limiter
- **Vị trí thư mục:** [feature1_rate_limiter](file:///d:/UDPT/redis-project/feature1_rate_limiter)
- **Kiến trúc:** Dùng thuật toán **Sliding Window Log (ZSET)**. Mỗi request lưu timestamp ở dạng microsecond.
- **Tính Atomic:** Toàn bộ logic kiểm tra và cập nhật được đóng gói trong một **Lua script** chạy trực tiếp trên Redis Engine để tránh race condition giữa các server instances.
- **Demo Phân Tán:** Chạy cùng lúc **3 FastAPI server** độc lập (port 8001, 8002, 8003). Dashboard sẽ gửi luân phiên (Load Balancing) qua các port này, chứng minh dù request gửi đi đâu thì bộ đếm vẫn đồng bộ hoàn hảo nhờ Redis Master.
- **Cách Chạy:**
  ```bash
  python feature1_rate_limiter/run_servers.py
  ```
  👉 Mở Trình duyệt: **[http://localhost:8001](http://localhost:8001)**

### ⚙️ Feature 2: Distributed Task Queue & Worker System
- **Vị trí thư mục:** [feature2_task_queue](file:///d:/UDPT/redis-project/feature2_task_queue)
- **Kiến trúc:** Xây dựng hàng đợi công việc sử dụng **Redis Streams** với cơ chế Consumer Group.
- **Độ tin cậy (At-Least-Once):** Worker chỉ gửi `xack` sau khi hoàn tất xử lý. Nếu crash, task sẽ quay lại PEL (Pending Entries List) để xử lý tiếp.
- **Cách ly lỗi (DLQ):** Khi task thất bại quá 3 lần, nó sẽ được chuyển sang **Dead Letter Queue (DLQ)** để tránh nghẽn hàng đợi chính.
- **Tự động đăng ký (Worker Discovery):** Worker gửi heartbeat cập nhật chỉ số của mình vào Redis. Dashboard tự động hiển thị các worker đang hoạt động trong thời gian thực.
- **Cách Chạy:**
  1. Khởi động Dashboard:
     ```bash
     python feature2_task_queue/run_dashboard.py
     ```
     👉 Mở Trình duyệt: **[http://localhost:8002](http://localhost:8002)**
  2. Mở thêm các terminal khác để chạy Worker:
     ```bash
     python feature2_task_queue/worker.py worker-A
     python feature2_task_queue/worker.py worker-B
     ```
  3. Gửi Task hoặc chọn "Tạo nhanh 10 Tasks ngẫu nhiên" trên UI để theo dõi phân chia tải!

