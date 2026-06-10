"""
Ngày 2 - Redis Streams: Distributed Task Processing
=====================================================
Mục tiêu: Hiểu Redis Streams — cơ chế phân phối công việc
          cho nhiều worker xử lý song song.

Cách chạy (mở 4 terminal):
  Terminal 1: python experiments/03_streams_producer.py
  Terminal 2: python experiments/03_streams_worker.py worker-A
  Terminal 3: python experiments/03_streams_worker.py worker-B
  Terminal 4: python experiments/03_streams_worker.py worker-C
"""

import redis
import time
import random
import sys
import json

STREAM_NAME = "job_stream"
GROUP_NAME = "worker_pool"

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def setup_consumer_group():
    """Tạo consumer group (chỉ cần 1 lần)"""
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, id='0', mkstream=True)
        print(f"✅ Consumer group '{GROUP_NAME}' created")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"ℹ️  Consumer group '{GROUP_NAME}' already exists")
        else:
            raise

def producer():
    """Gửi jobs vào stream"""
    setup_consumer_group()
    
    job_types = [
        ("resize_image",    0.5, "Resize ảnh về kích thước chuẩn"),
        ("send_email",      0.3, "Gửi email thông báo"),
        ("generate_report", 2.0, "Tạo báo cáo PDF"),
        ("process_payment", 1.0, "Xử lý thanh toán"),
        ("compress_video",  3.0, "Nén video"),
    ]
    
    print("=" * 55)
    print("  PRODUCER — Gửi jobs vào Redis Stream")
    print("=" * 55)
    print(f"Stream: '{STREAM_NAME}' | Group: '{GROUP_NAME}'\n")
    
    for i in range(15):
        job_type, duration, description = random.choice(job_types)
        job = {
            "job_id":      f"JOB-{i+1:03d}",
            "type":        job_type,
            "description": description,
            "duration":    str(duration),   # Thời gian giả lập xử lý
            "priority":    str(random.randint(1, 5)),
            "payload":     json.dumps({"param": f"value_{i}"}),
            "created_at":  str(time.time())
        }
        
        msg_id = r.xadd(STREAM_NAME, job)
        print(f"📤 Sent [{job['job_id']}] {job_type} (priority={job['priority']}) → {msg_id}")
        time.sleep(0.3)
    
    print(f"\n✅ Đã gửi 15 jobs! Stream length: {r.xlen(STREAM_NAME)}")
    print("   Kiểm tra workers đang xử lý...")


def worker(worker_id: str):
    """Worker xử lý jobs từ stream"""
    # Worker tự tạo group nếu chưa có (không cần producer chạy trước)
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, id='0', mkstream=True)
    except redis.exceptions.ResponseError:
        pass  # Group đã tồn tại → bình thường

    print("=" * 55)
    print(f"  WORKER [{worker_id}] — Chờ nhận jobs...")
    print("=" * 55)
    print(f"Listening on stream: '{STREAM_NAME}'\n")
    
    processed = 0
    failed = 0
    
    while True:
        try:
            # Lấy job mới từ stream (blocking 3 giây)
            messages = r.xreadgroup(
                groupname=GROUP_NAME,
                consumername=worker_id,
                streams={STREAM_NAME: ">"},  # ">" = chỉ lấy chưa deliver cho ai
                count=1,
                block=3000  # Chờ 3 giây nếu không có job
            )
            
            if not messages:
                print(f"[{worker_id}] ⏳ No jobs available. Processed so far: {processed}")
                # Sau 2 lần không có job thì dừng (cho demo)
                if processed > 0:
                    break
                continue
            
            for stream_name, msg_list in messages:
                for msg_id, job in msg_list:
                    print(f"[{worker_id}] 🔄 START  [{job['job_id']}] {job['type']}")
                    
                    # Giả lập thời gian xử lý
                    duration = float(job['duration'])
                    time.sleep(duration)
                    
                    # Giả lập lỗi ngẫu nhiên 10%
                    if random.random() < 0.1:
                        failed += 1
                        print(f"[{worker_id}] ❌ FAILED [{job['job_id']}] — Moving to dead letter queue")
                        # Gửi vào dead letter queue để retry sau
                        r.xadd(f"{STREAM_NAME}:dead_letter", {
                            **job,
                            "failed_by": worker_id,
                            "failed_at": str(time.time())
                        })
                    else:
                        processed += 1
                        print(f"[{worker_id}] ✅ DONE   [{job['job_id']}] {job['type']} ({duration}s)")
                    
                    # Acknowledge — báo đã xử lý (dù thành công hay thất bại)
                    r.xack(STREAM_NAME, GROUP_NAME, msg_id)
        
        except KeyboardInterrupt:
            break
    
    print(f"\n[{worker_id}] 🏁 Stopped. Processed: {processed}, Failed: {failed}")


def show_stats():
    """Hiển thị thống kê stream"""
    print("\n📊 Stream Statistics:")
    print(f"  Stream length: {r.xlen(STREAM_NAME)}")
    
    try:
        groups = r.xinfo_groups(STREAM_NAME)
        for group in groups:
            print(f"  Group '{group['name']}':")
            print(f"    - Pending messages: {group['pending']}")
            print(f"    - Consumers: {group['consumers']}")
    except Exception:
        pass
    
    dead_letter_len = r.xlen(f"{STREAM_NAME}:dead_letter") if r.exists(f"{STREAM_NAME}:dead_letter") else 0
    print(f"  Dead letter queue: {dead_letter_len} messages")


# ─── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    is_worker = len(sys.argv) > 1 and sys.argv[1].startswith("worker")

    if is_worker:
        # Worker mode: KHÔNG xóa stream, chỉ xử lý jobs
        worker(sys.argv[1])
        show_stats()
    else:
        # Producer mode: xóa stream cũ để demo sạch, rồi gửi jobs mới
        r.delete(STREAM_NAME, f"{STREAM_NAME}:dead_letter")
        producer()
        print("\n💡 Bây giờ mở 3 terminal và chạy:")
        print("   python experiments/03_streams.py worker-A")
        print("   python experiments/03_streams.py worker-B")
        print("   python experiments/03_streams.py worker-C")
