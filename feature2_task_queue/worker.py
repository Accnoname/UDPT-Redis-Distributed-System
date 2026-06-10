# -*- coding: utf-8 -*-
import redis
import time
import sys
import os
import random
import argparse

STREAM_NAME = "task_stream"
GROUP_NAME = "worker_group"
STATS_KEY_PREFIX = "worker:stats"
RETRY_KEY_PREFIX = "task:retries"
DLQ_KEY = "task_dlq"
COMPLETED_KEY = "tasks_completed_count"

def setup_worker(r: redis.Redis):
    # Tạo consumer group nếu chưa tồn tại
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise e

def update_worker_stats(r: redis.Redis, worker_id: str, status: str, job_id: str = "", success_inc: int = 0, fail_inc: int = 0):
    stats_key = f"{STATS_KEY_PREFIX}:{worker_id}"
    r.hset(stats_key, mapping={
        "status": status,
        "last_active": int(time.time()),
        "current_job": job_id
    })
    if success_inc > 0:
        r.hincrby(stats_key, "success_count", success_inc)
    if fail_inc > 0:
        r.hincrby(stats_key, "failed_count", fail_inc)
    # Set TTL cho worker stats để tự xóa nếu worker tắt (heartbeat timeout)
    r.expire(stats_key, 60)

def main():
    parser = argparse.ArgumentParser(description="Redis Stream Worker")
    parser.add_argument("name", nargs="?", default="worker-A", help="Tên của worker")
    args = parser.parse_args()
    
    worker_id = args.name
    
    # Kết nối tới Redis Master
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    setup_worker(r)
    
    # Khởi tạo stats cho worker
    r.hset(f"{STATS_KEY_PREFIX}:{worker_id}", mapping={
        "status": "Idle",
        "success_count": 0,
        "failed_count": 0,
        "current_job": ""
    })
    
    print("=" * 60)
    print(f"👷 Worker [{worker_id}] đã sẵn sàng xử lý Jobs...")
    print(f"   Stream: '{STREAM_NAME}' | Group: '{GROUP_NAME}'")
    print("=" * 60)
    
    try:
        while True:
            update_worker_stats(r, worker_id, "Idle")
            
            # 1. Đọc tin nhắn mới từ stream (">" nghĩa là chỉ lấy tin chưa gửi cho ai)
            messages = r.xreadgroup(
                groupname=GROUP_NAME,
                consumername=worker_id,
                streams={STREAM_NAME: ">"},
                count=1,
                block=1000 # Block 1 giây chờ tin
            )
            
            # 2. Nếu không có tin nhắn mới, thử kiểm tra tin nhắn PENDING (chưa xử lý xong của worker này)
            if not messages:
                messages = r.xreadgroup(
                    groupname=GROUP_NAME,
                    consumername=worker_id,
                    streams={STREAM_NAME: "0"}, # "0" nghĩa là lấy các tin nhắn pending
                    count=1,
                    block=100
                )
                
            if messages:
                for stream, msg_list in messages:
                    for msg_id, job in msg_list:
                        job_id = job.get("id", "unknown")
                        job_type = job.get("type", "generic")
                        print(f"\n📥 [{worker_id}] Nhận: Job {job_id} ({job_type})")
                        
                        update_worker_stats(r, worker_id, "Processing", job_id)
                        
                        # Giả lập thời gian xử lý (1.5 - 3 giây)
                        processing_time = random.uniform(1.5, 3.0)
                        time.sleep(processing_time)
                        
                        # Giả lập lỗi ngẫu nhiên 15% để test retry & DLQ
                        is_failed = random.random() < 0.15
                        
                        if is_failed:
                            # Tăng số lần thử lại cho Job này
                            retry_count = r.hincrby(f"{RETRY_KEY_PREFIX}:{job_id}", "retries", 1)
                            r.expire(f"{RETRY_KEY_PREFIX}:{job_id}", 3600) # Lưu lịch sử retry trong 1 giờ
                            
                            print(f"❌ [{worker_id}] Thất bại khi xử lý Job {job_id}. Lần lỗi thứ: {retry_count}")
                            
                            if retry_count >= 3:
                                # Chuyển Job sang Dead Letter Queue (DLQ)
                                r.xadd(DLQ_KEY, {
                                    "id": job_id,
                                    "type": job_type,
                                    "failed_by": worker_id,
                                    "error": "Failed after 3 attempts",
                                    "failed_at": str(time.time())
                                })
                                # Acknowledge ở stream chính để không bị lặp vô hạn
                                r.xack(STREAM_NAME, GROUP_NAME, msg_id)
                                r.xdel(STREAM_NAME, msg_id) # Xóa khỏi stream gốc để giải phóng bộ nhớ
                                
                                print(f"⚠️  [{worker_id}] Job {job_id} lỗi quá 3 lần. Đã chuyển sang DLQ '{DLQ_KEY}'")
                                update_worker_stats(r, worker_id, "Idle", fail_inc=1)
                            else:
                                # Không XACK, tin nhắn vẫn nằm trong PEL (Pending Entries List)
                                # Lần sau worker khác hoặc chính worker này sẽ quét và xử lý lại
                                update_worker_stats(r, worker_id, "Idle")
                        else:
                            # Xử lý thành công
                            r.xack(STREAM_NAME, GROUP_NAME, msg_id)
                            r.xdel(STREAM_NAME, msg_id) # Xóa khỏi stream để giải phóng bộ nhớ
                            
                            # Tăng tổng counter completed
                            r.incrby(COMPLETED_KEY, 1)
                            
                            print(f"✅ [{worker_id}] Thành công: Job {job_id} (xử lý mất {processing_time:.1f}s)")
                            update_worker_stats(r, worker_id, "Idle", success_inc=1)
            
            # Gửi tín hiệu sống (heartbeat)
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Worker [{worker_id}] đang tắt...")
        # Xóa stats của worker khi tắt
        r.delete(f"{STATS_KEY_PREFIX}:{worker_id}")
        print("Bye!")

if __name__ == "__main__":
    main()
