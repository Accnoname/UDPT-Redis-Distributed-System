# -*- coding: utf-8 -*-
import os
import sys
import redis
import time
import uuid
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Distributed Task Queue Dashboard")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

STREAM_NAME = "task_stream"
GROUP_NAME = "worker_group"
STATS_KEY_PREFIX = "worker:stats"
DLQ_KEY = "task_dlq"
COMPLETED_KEY = "tasks_completed_count"

class TaskRequest(BaseModel):
    task_type: str

@app.get("/")
def get_index():
    # Serve dashboard UI
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Task Queue API is running. index.html not found."}

@app.post("/api/tasks")
def add_task(request: TaskRequest):
    try:
        task_id = f"JOB-{uuid.uuid4().hex[:6].upper()}"
        task_data = {
            "id": task_id,
            "type": request.task_type,
            "created_at": str(time.time())
        }
        # Thêm task vào Redis Stream
        msg_id = redis_client.xadd(STREAM_NAME, task_data)
        return {
            "status": "success",
            "task_id": task_id,
            "msg_id": msg_id,
            "type": request.task_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/generate-bulk")
def generate_bulk(count: int = 10):
    try:
        job_types = ["send_email", "resize_image", "generate_report", "compress_video"]
        generated = []
        for _ in range(count):
            task_id = f"JOB-{uuid.uuid4().hex[:6].upper()}"
            task_type = random.choice(job_types)
            task_data = {
                "id": task_id,
                "type": task_type,
                "created_at": str(time.time())
            }
            msg_id = redis_client.xadd(STREAM_NAME, task_data)
            generated.append({"task_id": task_id, "type": task_type})
        return {"status": "success", "count": count, "tasks": generated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
def get_stats():
    try:
        # 1. Lấy kích thước queue hiện tại (chưa được xử lý)
        queue_size = redis_client.xlen(STREAM_NAME)
        
        # 2. Lấy số lượng jobs hoàn thành
        completed_val = redis_client.get(COMPLETED_KEY)
        completed_count = int(completed_val) if completed_val else 0
        
        # 3. Lấy thông tin Pending Jobs (đã gửi cho worker nhưng chưa nhận được XACK)
        pending_count = 0
        try:
            pending_info = redis_client.xpending(STREAM_NAME, GROUP_NAME)
            pending_count = pending_info["pending"]
        except redis.exceptions.ResponseError as e:
            # Nếu group chưa được tạo bởi bất kỳ worker nào
            if "NOGROUP" in str(e):
                pass
        
        # 4. Lấy danh sách jobs trong Dead Letter Queue (DLQ)
        dlq_items = []
        try:
            dlq_raw = redis_client.xrange(DLQ_KEY, count=100)
            for msg_id, fields in dlq_raw:
                dlq_items.append({
                    "msg_id": msg_id,
                    "id": fields.get("id"),
                    "type": fields.get("type"),
                    "failed_by": fields.get("failed_by"),
                    "error": fields.get("error"),
                    "failed_at": fields.get("failed_at")
                })
        except Exception:
            pass
            
        # 5. Lấy danh sách và thống kê các workers đang active
        workers = []
        worker_keys = redis_client.keys(f"{STATS_KEY_PREFIX}:*")
        for key in worker_keys:
            worker_name = key.split(":")[-1]
            stats = redis_client.hgetall(key)
            if stats:
                workers.append({
                    "name": worker_name,
                    "status": stats.get("status", "Unknown"),
                    "success_count": int(stats.get("success_count", 0)),
                    "failed_count": int(stats.get("failed_count", 0)),
                    "current_job": stats.get("current_job", ""),
                    "last_active": int(stats.get("last_active", 0))
                })
                
        # Sắp xếp worker theo tên
        workers.sort(key=lambda w: w["name"])
        
        return {
            "queue_size": queue_size,
            "completed_count": completed_count,
            "pending_count": pending_count,
            "dlq_count": len(dlq_items),
            "dlq_items": dlq_items,
            "workers": workers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-dlq")
def clear_dlq():
    try:
        redis_client.delete(DLQ_KEY)
        return {"status": "success", "message": "Dead Letter Queue cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-all")
def reset_all():
    try:
        # Xóa các key liên quan đến stats và stream
        redis_client.delete(STREAM_NAME)
        redis_client.delete(DLQ_KEY)
        redis_client.delete(COMPLETED_KEY)
        
        worker_keys = redis_client.keys(f"{STATS_KEY_PREFIX}:*")
        if worker_keys:
            redis_client.delete(*worker_keys)
            
        retry_keys = redis_client.keys("task:retries:*")
        if retry_keys:
            redis_client.delete(*retry_keys)
            
        # Xóa Consumer Group cũ để setup lại sạch sẽ
        try:
            redis_client.xgroup_destroy(STREAM_NAME, GROUP_NAME)
        except Exception:
            pass
            
        return {"status": "success", "message": "Reset all queue statistics and streams"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
