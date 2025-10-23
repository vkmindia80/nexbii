from fastapi import APIRouter, Depends, HTTPException, status
from ...core.security import get_current_user
from ...services.cache_service import CacheService

router = APIRouter()

@router.get("/stats")
async def get_cache_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get cache performance statistics
    
    Returns:
    - Cache hit rate
    - Total hits and misses
    - Number of cached queries
    - Memory usage
    """
    cache_service = CacheService()
    stats = cache_service.get_cache_stats()
    
    return {
        "success": True,
        "data": stats
    }

@router.delete("/clear")
async def clear_cache(
    current_user: dict = Depends(get_current_user)
):
    """
    Clear all cached query results
    
    Requires authentication.
    """
    cache_service = CacheService()
    
    if not cache_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service is not available"
        )
    
    success = cache_service.clear_all_cache()
    
    if success:
        return {
            "success": True,
            "message": "All cache cleared successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )

@router.delete("/datasource/{datasource_id}")
async def clear_datasource_cache(
    datasource_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Clear cached queries for a specific datasource
    
    Args:
        datasource_id: ID of the datasource
    """
    cache_service = CacheService()
    
    if not cache_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service is not available"
        )
    
    deleted_count = cache_service.invalidate_datasource_cache(datasource_id)
    
    return {
        "success": True,
        "message": f"Cleared {deleted_count} cached queries for datasource",
        "deleted_count": deleted_count
    }

@router.post("/reset-stats")
async def reset_cache_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Reset cache statistics counters
    """
    cache_service = CacheService()
    
    if not cache_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache service is not available"
        )
    
    success = cache_service.reset_stats()
    
    if success:
        return {
            "success": True,
            "message": "Cache statistics reset successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset cache statistics"
        )
