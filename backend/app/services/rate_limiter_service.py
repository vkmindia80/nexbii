import time
from typing import Optional
from redis import Redis
from ..core.config import settings
from fastapi import HTTPException, status

class RateLimiterService:
    """
    Redis-based rate limiting service
    Implements sliding window rate limiting per API key
    """
    
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Redis for rate limiting: {e}")
            self.redis_client = None
    
    def _get_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limit tracking"""
        return f"ratelimit:{identifier}:{window}"
    
    def check_rate_limit(
        self,
        identifier: str,
        limit_per_minute: int,
        limit_per_hour: int,
        limit_per_day: int
    ) -> dict:
        """
        Check if request is within rate limits
        
        Args:
            identifier: Unique identifier (API key ID or user ID)
            limit_per_minute: Max requests per minute
            limit_per_hour: Max requests per hour
            limit_per_day: Max requests per day
        
        Returns:
            dict with rate limit info
        
        Raises:
            HTTPException: If rate limit is exceeded
        """
        if not self.redis_client:
            # If Redis is not available, allow all requests (fail open)
            return {
                "limited": False,
                "remaining_minute": limit_per_minute,
                "remaining_hour": limit_per_hour,
                "remaining_day": limit_per_day
            }
        
        current_time = int(time.time())
        
        # Check minute window
        minute_key = self._get_key(identifier, f"minute:{current_time // 60}")
        minute_count = self._increment_counter(minute_key, 60)
        
        # Check hour window
        hour_key = self._get_key(identifier, f"hour:{current_time // 3600}")
        hour_count = self._increment_counter(hour_key, 3600)
        
        # Check day window
        day_key = self._get_key(identifier, f"day:{current_time // 86400}")
        day_count = self._increment_counter(day_key, 86400)
        
        # Calculate remaining requests
        remaining_minute = max(0, limit_per_minute - minute_count + 1)  # +1 because we already incremented
        remaining_hour = max(0, limit_per_hour - hour_count + 1)
        remaining_day = max(0, limit_per_day - day_count + 1)
        
        # Check if any limit is exceeded
        if minute_count > limit_per_minute:
            reset_time = ((current_time // 60) + 1) * 60
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit_per_minute} requests per minute",
                headers={
                    "X-RateLimit-Limit": str(limit_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - current_time)
                }
            )
        
        if hour_count > limit_per_hour:
            reset_time = ((current_time // 3600) + 1) * 3600
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit_per_hour} requests per hour",
                headers={
                    "X-RateLimit-Limit": str(limit_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - current_time)
                }
            )
        
        if day_count > limit_per_day:
            reset_time = ((current_time // 86400) + 1) * 86400
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit_per_day} requests per day",
                headers={
                    "X-RateLimit-Limit": str(limit_per_day),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - current_time)
                }
            )
        
        return {
            "limited": False,
            "remaining_minute": remaining_minute,
            "remaining_hour": remaining_hour,
            "remaining_day": remaining_day,
            "reset_minute": ((current_time // 60) + 1) * 60,
            "reset_hour": ((current_time // 3600) + 1) * 3600,
            "reset_day": ((current_time // 86400) + 1) * 86400
        }
    
    def _increment_counter(self, key: str, ttl: int) -> int:
        """
        Increment counter in Redis with TTL
        
        Args:
            key: Redis key
            ttl: Time to live in seconds
        
        Returns:
            Current count after increment
        """
        try:
            # Increment counter
            count = self.redis_client.incr(key)
            
            # Set expiration on first increment
            if count == 1:
                self.redis_client.expire(key, ttl)
            
            return count
        except Exception as e:
            print(f"⚠️  Warning: Redis error during rate limiting: {e}")
            return 0
    
    def get_current_usage(
        self,
        identifier: str
    ) -> dict:
        """
        Get current usage without incrementing
        """
        if not self.redis_client:
            return {
                "minute": 0,
                "hour": 0,
                "day": 0
            }
        
        current_time = int(time.time())
        
        minute_key = self._get_key(identifier, f"minute:{current_time // 60}")
        hour_key = self._get_key(identifier, f"hour:{current_time // 3600}")
        day_key = self._get_key(identifier, f"day:{current_time // 86400}")
        
        try:
            minute_count = int(self.redis_client.get(minute_key) or 0)
            hour_count = int(self.redis_client.get(hour_key) or 0)
            day_count = int(self.redis_client.get(day_key) or 0)
            
            return {
                "minute": minute_count,
                "hour": hour_count,
                "day": day_count
            }
        except Exception:
            return {
                "minute": 0,
                "hour": 0,
                "day": 0
            }
    
    def reset_limits(self, identifier: str):
        """
        Reset rate limits for an identifier (useful for testing)
        """
        if not self.redis_client:
            return
        
        current_time = int(time.time())
        
        minute_key = self._get_key(identifier, f"minute:{current_time // 60}")
        hour_key = self._get_key(identifier, f"hour:{current_time // 3600}")
        day_key = self._get_key(identifier, f"day:{current_time // 86400}")
        
        try:
            self.redis_client.delete(minute_key, hour_key, day_key)
        except Exception as e:
            print(f"⚠️  Warning: Could not reset rate limits: {e}")


# Global rate limiter instance
rate_limiter = RateLimiterService()
