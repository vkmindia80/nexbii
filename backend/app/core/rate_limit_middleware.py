from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..services.rate_limiter_service import rate_limiter
from ..models.api_key import APIKey
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API requests
    """
    
    # Paths to exclude from rate limiting
    EXCLUDED_PATHS = [
        "/api/health",
        "/api",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/socket.io"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)
        
        # Check if request has API key authentication
        api_key = None
        if hasattr(request.state, 'api_key'):
            api_key = request.state.api_key
        
        # Only apply rate limiting if using API key
        if api_key and isinstance(api_key, APIKey):
            try:
                # Check rate limits
                rate_info = rate_limiter.check_rate_limit(
                    identifier=api_key.id,
                    limit_per_minute=api_key.rate_limit_per_minute,
                    limit_per_hour=api_key.rate_limit_per_hour,
                    limit_per_day=api_key.rate_limit_per_day
                )
                
                # Process request
                start_time = time.time()
                response = await call_next(request)
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Add rate limit headers
                response.headers["X-RateLimit-Limit-Minute"] = str(api_key.rate_limit_per_minute)
                response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["remaining_minute"])
                response.headers["X-RateLimit-Reset-Minute"] = str(rate_info["reset_minute"])
                
                response.headers["X-RateLimit-Limit-Hour"] = str(api_key.rate_limit_per_hour)
                response.headers["X-RateLimit-Remaining-Hour"] = str(rate_info["remaining_hour"])
                response.headers["X-RateLimit-Reset-Hour"] = str(rate_info["reset_hour"])
                
                response.headers["X-RateLimit-Limit-Day"] = str(api_key.rate_limit_per_day)
                response.headers["X-RateLimit-Remaining-Day"] = str(rate_info["remaining_day"])
                response.headers["X-RateLimit-Reset-Day"] = str(rate_info["reset_day"])
                
                # Log usage (this will be done in the API key middleware)
                request.state.response_time_ms = response_time_ms
                
                return response
                
            except Exception as e:
                # If it's a rate limit exception, return 429
                if hasattr(e, 'status_code') and e.status_code == 429:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": str(e.detail)},
                        headers=dict(e.headers) if hasattr(e, 'headers') else {}
                    )
                raise
        
        # For non-API-key requests, just pass through
        return await call_next(request)
