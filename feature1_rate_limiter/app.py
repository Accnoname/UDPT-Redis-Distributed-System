# -*- coding: utf-8 -*-
import os
import sys
import redis
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

@app.post("/api/reset")
def reset_limit(client_id: str = "default_client"):
    try:
        redis_client.delete(f"ratelimit:{client_id}")
        return {"status": "success", "message": f"Reset limit for client '{client_id}'", "server_port": PORT}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
