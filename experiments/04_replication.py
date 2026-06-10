"""
Ngày 3 - Replication: Master-Replica Architecture
===================================================
Mục tiêu: Kiểm chứng Redis Replication hoạt động như thế nào.
          Write → Master, Read → Replicas.

Yêu cầu: docker-compose -f docker-compose-replica.yml up -d

Chạy: python experiments/04_replication.py
"""

import redis
import time

# ─── Kết nối tất cả nodes ────────────────────────────────────────
master    = redis.Redis(host='localhost', port=6379, decode_responses=True)
replica1  = redis.Redis(host='localhost', port=6380, decode_responses=True)
replica2  = redis.Redis(host='localhost', port=6381, decode_responses=True)

nodes = {
    "Master  (6379)": master,
    "Replica1(6380)": replica1,
    "Replica2(6381)": replica2,
}

def separator(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)

# ─── Kiểm tra kết nối ────────────────────────────────────────────
separator("1. Kiểm tra kết nối tất cả nodes")
for name, node in nodes.items():
    try:
        node.ping()
        role = node.info('replication')['role']
        print(f"  ✅ {name} → role: {role}")
    except Exception as e:
        print(f"  ❌ {name} → {e}")
        print("     Hãy chạy: docker-compose -f docker-compose-replica.yml up -d")
        exit(1)

# ─── Thông tin replication ────────────────────────────────────────
separator("2. Thông tin Replication của Master")
rep_info = master.info('replication')
print(f"  Role:               {rep_info['role']}")
print(f"  Connected replicas: {rep_info['connected_slaves']}")
for i in range(rep_info['connected_slaves']):
    slave = rep_info[f'slave{i}']
    print(f"  Replica {i+1}:         {slave}")

# ─── Test 1: Write vào Master → tự động sync Replicas ────────────
separator("3. Demo Replication: Write Master → Sync Replicas")

print("  Ghi dữ liệu vào MASTER...")
test_data = {
    "server:info":    "Redis Distributed Demo",
    "app:version":    "1.0.0",
    "user:count":     "1000",
}
for key, val in test_data.items():
    master.set(key, val)
    master.hset("config", mapping={"env": "production", "region": "asia"})

print("  Đã ghi! Chờ replication sync (100ms)...")
time.sleep(0.1)

print("\n  Đọc từ tất cả nodes:")
for key in test_data.keys():
    print(f"\n  Key: '{key}'")
    for name, node in nodes.items():
        val = node.get(key)
        print(f"    {name}: {val}")

# ─── Test 2: Replica là READ-ONLY ────────────────────────────────
separator("4. Demo: Replica là READ-ONLY")
print("  Thử ghi vào Replica1 (phải bị từ chối)...")
try:
    replica1.set("test_write", "should_fail")
    print("  ⚠️  Unexpected: Write succeeded!")
except redis.exceptions.ReadOnlyError:
    print("  ✅ ReadOnlyError — Replicas không cho phép WRITE!")
    print("     → Đây là thiết kế: chỉ Master nhận write request")

# ─── Test 3: Read Scaling ─────────────────────────────────────────
separator("5. Demo: Read Scaling với nhiều Replicas")
print("  Mô phỏng load balancing: phân tán 9 read request")

import random
all_replicas = [replica1, replica2]
replica_names = ["Replica1", "Replica2"]
request_count = {name: 0 for name in replica_names}

for i in range(9):
    # Load balancer chọn ngẫu nhiên replica
    idx = i % 2  # Round-robin
    chosen = replica_names[idx]
    replica = all_replicas[idx]
    
    val = replica.get("server:info")
    request_count[chosen] += 1
    print(f"  Request #{i+1} → {chosen}: '{val}'")

print(f"\n  Phân phối: {request_count}")
print("  → Mỗi Replica phục vụ 1/2 read request! Master được giảm tải.")

# ─── Test 4: Replication lag ─────────────────────────────────────
separator("6. Demo: Đo Replication Lag")
print("  Ghi 100 keys vào Master và đo thời gian sync...")

start = time.time()
for i in range(100):
    master.set(f"lag_test:{i}", f"value_{i}")

write_done = time.time()

# Đợi cho đến khi Replica có đủ data
while True:
    count = sum(1 for i in range(100) if replica1.get(f"lag_test:{i}"))
    if count == 100:
        break
    time.sleep(0.001)

sync_done = time.time()

write_time = (write_done - start) * 1000
lag_time   = (sync_done - write_done) * 1000
print(f"  ✅ Write 100 keys:     {write_time:.1f}ms")
print(f"  ✅ Replication lag:    {lag_time:.1f}ms")
print(f"  📌 Replication là ASYNC → có thể có lag nhỏ")

# ─── Tổng kết ─────────────────────────────────────────────────────
separator("Tổng kết — Lợi ích của Replication")
print("""
  ✅ High Availability:
     Nếu Master chết → Replica được promote lên làm Master
     (Dùng Redis Sentinel để tự động hóa)

  ✅ Read Scaling:
     Nhiều Replica = nhiều máy phục vụ read request
     Master chỉ phải xử lý write

  ✅ Data Redundancy:
     Dữ liệu có nhiều bản sao → không mất khi 1 node chết

  ❌ Write Bottleneck:
     Vẫn chỉ có 1 Master cho write
     → Giải pháp: Redis CLUSTER (sharding)
""")
