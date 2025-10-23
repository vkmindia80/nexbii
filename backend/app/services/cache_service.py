import redis
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.config import settings

class CacheService:
    """
    Redis-based caching service for query results
    
    Features:
    - Query result caching with configurable TTL
    - Cache key generation based on query + datasource
    - Cache invalidation strategies
    - Cache hit rate monitoring
    - Performance optimization
    """
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"⚠️  Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def _generate_cache_key(self, datasource_id: str, query: str, limit: int = 1000) -> str:
        """
        Generate a unique cache key based on datasource, query, and limit
        
        Args:
            datasource_id: ID of the datasource
            query: SQL query string
            limit: Query result limit
            
        Returns:
            SHA256 hash as cache key
        """
        # Normalize query (remove extra whitespace, convert to lowercase)
        normalized_query = ' '.join(query.lower().split())
        
        # Create unique identifier
        key_data = f"{datasource_id}:{normalized_query}:{limit}"
        
        # Generate hash
        cache_key = hashlib.sha256(key_data.encode()).hexdigest()
        
        return f"query:{cache_key}"
    
    def get_cached_result(self, datasource_id: str, query: str, limit: int = 1000) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached query result
        
        Args:
            datasource_id: ID of the datasource
            query: SQL query string
            limit: Query result limit
            
        Returns:
            Cached result dict or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._generate_cache_key(datasource_id, query, limit)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                # Increment hit counter
                self.redis_client.incr("cache:hits")
                
                result = json.loads(cached_data)
                result['from_cache'] = True
                result['cached_at'] = result.get('cached_at', datetime.utcnow().isoformat())
                
                return result
            else:
                # Increment miss counter
                self.redis_client.incr("cache:misses")
                return None
                
        except Exception as e:
            print(f"⚠️  Cache retrieval error: {e}")
            return None
    
    def set_cached_result(
        self,
        datasource_id: str,
        query: str,
        result: Dict[str, Any],
        limit: int = 1000,
        ttl: int = 900  # 15 minutes default
    ) -> bool:
        """
        Store query result in cache with TTL
        
        Args:
            datasource_id: ID of the datasource
            query: SQL query string
            result: Query result to cache
            limit: Query result limit
            ttl: Time to live in seconds (default: 900 = 15 minutes)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(datasource_id, query, limit)
            
            # Add metadata
            cache_data = {
                **result,
                'cached_at': datetime.utcnow().isoformat(),
                'datasource_id': datasource_id
            }
            
            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            # Track datasource-query mapping for invalidation
            datasource_key = f"datasource:{datasource_id}:queries"
            self.redis_client.sadd(datasource_key, cache_key)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Cache storage error: {e}")
            return False
    
    def invalidate_datasource_cache(self, datasource_id: str) -> int:
        """
        Invalidate all cached queries for a specific datasource
        
        Args:
            datasource_id: ID of the datasource
            
        Returns:
            Number of cache entries invalidated
        """
        if not self.enabled:
            return 0
        
        try:
            datasource_key = f"datasource:{datasource_id}:queries"
            
            # Get all query cache keys for this datasource
            query_keys = self.redis_client.smembers(datasource_key)
            
            if not query_keys:
                return 0
            
            # Delete all query caches
            deleted_count = self.redis_client.delete(*query_keys)
            
            # Delete the datasource tracking set
            self.redis_client.delete(datasource_key)
            
            print(f"✅ Invalidated {deleted_count} cache entries for datasource {datasource_id}")
            
            return deleted_count
            
        except Exception as e:
            print(f"⚠️  Cache invalidation error: {e}")
            return 0
    
    def clear_all_cache(self) -> bool:
        """
        Clear all query caches
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Get all query cache keys
            query_keys = self.redis_client.keys("query:*")
            datasource_keys = self.redis_client.keys("datasource:*")
            
            all_keys = query_keys + datasource_keys
            
            if all_keys:
                self.redis_client.delete(*all_keys)
                print(f"✅ Cleared {len(all_keys)} cache entries")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Dictionary containing cache statistics
        """
        if not self.enabled:
            return {
                'enabled': False,
                'status': 'disabled',
                'message': 'Redis caching is not available'
            }
        
        try:
            hits = int(self.redis_client.get("cache:hits") or 0)
            misses = int(self.redis_client.get("cache:misses") or 0)
            total_requests = hits + misses
            
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
            
            # Get cache size info
            query_keys = self.redis_client.keys("query:*")
            cached_queries = len(query_keys)
            
            # Get memory info
            memory_info = self.redis_client.info('memory')
            used_memory = memory_info.get('used_memory_human', 'N/A')
            
            return {
                'enabled': True,
                'status': 'active',
                'hits': hits,
                'misses': misses,
                'total_requests': total_requests,
                'hit_rate': round(hit_rate, 2),
                'cached_queries': cached_queries,
                'memory_used': used_memory,
                'redis_url': settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else settings.REDIS_URL
            }
            
        except Exception as e:
            return {
                'enabled': False,
                'status': 'error',
                'error': str(e)
            }
    
    def reset_stats(self) -> bool:
        """
        Reset cache statistics counters
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete("cache:hits", "cache:misses")
            return True
        except Exception as e:
            print(f"⚠️  Stats reset error: {e}")
            return False
