# -*- coding: utf-8 -*-
import redis
import time

class DistributedRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        # Lua script to run sliding window rate limiting atomically
        self.lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local clear_before = now - window

        -- 1. Xóa các request cũ ngoài window
        redis.call('ZREMRANGEBYSCORE', key, 0, clear_before)

        -- 2. Đếm số request hiện tại trong window
        local current_requests = redis.call('ZCARD', key)

        if current_requests < limit then
            -- 3. Thêm request hiện tại vào (value và score đều là timestamp)
            redis.call('ZADD', key, now, now)
            -- Thiết lập thời gian sống bằng độ rộng window để tự giải phóng bộ nhớ khi idle
            redis.call('EXPIRE', key, window)
            return {1, current_requests + 1} -- [allowed: 1 (True), current_count]
        else
            return {0, current_requests} -- [allowed: 0 (False), current_count]
        end
        """
        # Register the script
        self.limiter_script = self.redis.register_script(self.lua_script)

    def is_allowed(self, user_id: str, limit: int = 10, window_seconds: int = 10) -> tuple[bool, int, int]:
        """
        Kiểm tra xem user_id có được phép thực hiện request hay không.
        Trả về: (is_allowed, current_count, limit)
        """
        key = f"ratelimit:{user_id}"
        # Dùng microsecond timestamp để tránh trùng lặp khi ghi nhanh
        now_ms = int(time.time() * 1000)
        window_ms = window_seconds * 1000

        # Chạy script Lua trên Redis
        result = self.limiter_script(keys=[key], args=[now_ms, window_ms, limit])
        
        allowed = bool(result[0])
        current_count = result[1]
        
        return allowed, current_count, limit
