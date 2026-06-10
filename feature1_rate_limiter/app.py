# -*- coding: utf-8 -*-
import os
import sys
import redis
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from rate_limiter import DistributedRateLimiter

app = FastAPI(title="Distributed Rate Limiter Demo")

# CORS middleware to allow the frontend to easily call different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis Master (port 6379)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
limiter = DistributedRateLimiter(redis_client)

# Port of this server instance
PORT = int(os.getenv("PORT", 8001))

LOGS_KEY = "ratelimit:logs"

@app.get("/")
def get_index():
    # Serve the frontend index.html
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Rate Limiter API is running. index.html not found.", "port": PORT}

@app.get("/api/request")
def make_request(client_id: str = "default_client", limit: int = 10, window: int = 10):
    try:
        allowed, current_count, limit = limiter.is_allowed(client_id, limit, window)
        
        # Ghi log request vào Redis List dùng chung
        log_entry = {
            "timestamp": time.time(),
            "port": PORT,
            "client_id": client_id,
            "allowed": allowed,
            "current_count": current_count,
            "limit": limit
        }
        redis_client.lpush(LOGS_KEY, json.dumps(log_entry))
        redis_client.ltrim(LOGS_KEY, 0, 49) # Giới hạn lưu 50 logs gần nhất
        
        return {
            "allowed": allowed,
            "client_id": client_id,
            "current_count": current_count,
            "limit": limit,
            "window": window,
            "server_port": PORT,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
def get_status(client_id: str = "default_client", limit: int = 10, window: int = 10):
    try:
        key = f"ratelimit:{client_id}"
        # Dọn dẹp ZSET ngoài window để có số đếm chính xác
        now_ms = int(time.time() * 1000)
        window_ms = window * 1000
        redis_client.zremrangebyscore(key, 0, now_ms - window_ms)
        current_count = redis_client.zcard(key)
        return {
            "client_id": client_id,
            "current_count": current_count,
            "limit": limit,
            "window": window
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
def get_logs():
    try:
        # Lấy 50 logs gần nhất
        logs_raw = redis_client.lrange(LOGS_KEY, 0, -1)
        logs = [json.loads(log) for log in logs_raw]
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
def reset_limit(client_id: str = "default_client"):
    try:
        redis_client.delete(f"ratelimit:{client_id}")
        redis_client.delete(LOGS_KEY) # Xóa cả danh sách logs
        return {"status": "success", "message": f"Reset limit and logs for client '{client_id}'", "server_port": PORT}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

