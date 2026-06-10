# -*- coding: utf-8 -*-
"""
Ngày 1 - Thực nghiệm cơ bản Redis
===================================
Mục tiêu: Hiểu các kiểu dữ liệu Redis và tại sao chúng phù hợp
          cho hệ thống phân tán.

Chạy: python experiments/01_basics.py
Yêu cầu: Redis đang chạy trên localhost:6379
"""

import redis
import time

# ─── Kết nối Redis ───────────────────────────────────────────────
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def separator(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

# ─── 1. Kiểm tra kết nối ─────────────────────────────────────────
separator("1. Kết nối Redis")
try:
    r.ping()
    info = r.info('server')
    print(f"✅ Kết nối thành công!")
    print(f"   Redis version: {info['redis_version']}")
    print(f"   Mode: {info['redis_mode']}")
except redis.ConnectionError:
    print("❌ Không kết nối được Redis! Hãy chạy: docker-compose up -d")
    exit(1)

# ─── 2. STRING — Kiểu dữ liệu cơ bản nhất ───────────────────────
separator("2. STRING — Atomic Counter (quan trọng trong phân tán!)")

# INCR là atomic — nhiều server cùng INCR sẽ KHÔNG bị race condition
r.set("page_views", 0)
print("Giả lập 3 server cùng tăng counter:")
for server_id in range(1, 4):
    for _ in range(3):
        count = r.incr("page_views")
    print(f"  Server {server_id} đã tăng 3 lần → Total: {r.get('page_views')}")

print(f"\n📌 Tổng page views: {r.get('page_views')} (đúng = 9)")
print("   INCR là atomic → không bao giờ bị race condition!")

# TTL — Key tự xóa sau một thời gian
r.set("session:user123", "logged_in", ex=30)  # Hết hạn sau 30 giây
ttl = r.ttl("session:user123")
print(f"\n📌 Session key TTL: {ttl} giây → tự xóa sau {ttl}s")

# ─── 3. HASH — Lưu object có cấu trúc ───────────────────────────
separator("3. HASH — Lưu User Object")

users = [
    {"id": 1, "name": "Nguyen Van A", "email": "a@example.com", "score": 1500},
    {"id": 2, "name": "Tran Thi B",   "email": "b@example.com", "score": 2300},
    {"id": 3, "name": "Le Van C",     "email": "c@example.com", "score": 800},
]

for u in users:
    r.hset(f"user:{u['id']}", mapping={
        "name": u["name"],
        "email": u["email"],
        "score": u["score"]
    })

print("Đã lưu 3 users. Đọc lại:")
for i in range(1, 4):
    user = r.hgetall(f"user:{i}")
    print(f"  user:{i} → {user}")

# Cập nhật 1 field mà không cần đọc toàn bộ object
r.hset("user:1", "score", 1600)
print(f"\n📌 Cập nhật score user:1 → {r.hget('user:1', 'score')}")

# ─── 4. LIST — Task Queue đơn giản ───────────────────────────────
separator("4. LIST — Task Queue (FIFO)")

tasks = ["send_email:user1", "resize_image:photo.jpg", "generate_report:Q1", "process_payment:order999"]

print("Producer thêm tasks vào queue:")
for task in tasks:
    r.rpush("task_queue", task)
    print(f"  ➕ Pushed: {task}")

print(f"\nQueue size: {r.llen('task_queue')}")
print("\nWorker xử lý tasks (FIFO):")
while r.llen("task_queue") > 0:
    task = r.lpop("task_queue")
    print(f"  ▶️  Processing: {task}")
    time.sleep(0.1)

# ─── 5. SET — Quản lý trạng thái online ──────────────────────────
separator("5. SET — Online Users (không trùng lặp)")

# Nhiều server đều có thể add/remove user vào shared set
r.delete("online_users")
r.sadd("online_users", "user:1", "user:2", "user:3")
r.sadd("online_users", "user:1")  # Không bị duplicate!

print(f"Online users: {r.smembers('online_users')}")
print(f"Số lượng: {r.scard('online_users')}")
print(f"user:1 online? {r.sismember('online_users', 'user:1')}")

r.srem("online_users", "user:2")  # User logout
print(f"Sau khi user:2 logout: {r.smembers('online_users')}")

# ─── 6. SORTED SET — Leaderboard ─────────────────────────────────
separator("6. SORTED SET — Leaderboard / Xếp Hạng")

r.delete("leaderboard")
players = [("player1", 1500), ("player2", 2300), ("player3", 800),
           ("player4", 3100), ("player5", 1200)]

for name, score in players:
    r.zadd("leaderboard", {name: score})

print("Top 3 players:")
top3 = r.zrevrange("leaderboard", 0, 2, withscores=True)
for rank, (player, score) in enumerate(top3, 1):
    print(f"  #{rank} {player}: {int(score)} điểm")

# Thêm điểm realtime (atomic)
r.zincrby("leaderboard", 500, "player3")
print(f"\nSau khi player3 +500 điểm:")
print(f"  player3 mới: {int(r.zscore('leaderboard', 'player3'))} điểm")
print(f"  Rank của player3: #{r.zrevrank('leaderboard', 'player3') + 1}")

# ─── Tổng kết ─────────────────────────────────────────────────────
separator("Tổng kết — Tại sao Redis phù hợp hệ thống phân tán?")
print("""
✅ Atomic operations (INCR, SETNX, ZADD):
   → Nhiều server cùng thao tác không bị race condition

✅ Shared state:
   → Tất cả server đọc/ghi cùng 1 nơi → đồng nhất dữ liệu

✅ TTL (key tự xóa):
   → Không cần cleanup manual, tránh memory leak

✅ Pub/Sub & Streams:
   → Giao tiếp không đồng bộ giữa các service

✅ Replication & Clustering:
   → Scale out, không có single point of failure
""")
print(f"📊 Tổng số keys hiện tại: {r.dbsize()}")
