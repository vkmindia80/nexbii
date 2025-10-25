from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.query import Query
from ...models.datasource import DataSource
from ...schemas.query import (
    QueryCreate,
    QueryUpdate,
    QueryResponse,
    QueryExecute,
    QueryResult
)
from ...services.query_service import QueryService
from ...services.cache_service import CacheService

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def create_query(
    query_data: QueryCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = Query(
        name=query_data.name,
        description=query_data.description,
        datasource_id=query_data.datasource_id,
        query_type=query_data.query_type,
        query_config=query_data.query_config,
        sql_query=query_data.sql_query,
        created_by=current_user.id
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    
    return QueryResponse.from_orm(query)

@router.get("/", response_model=List[QueryResponse])
async def list_queries(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queries = db.query(Query).all()
    return [QueryResponse.from_orm(q) for q in queries]

@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    return QueryResponse.from_orm(query)

@router.post("/execute", response_model=QueryResult)
async def execute_query(
    execute_data: QueryExecute,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if query_id is provided
    if hasattr(execute_data, 'query_id') and execute_data.query_id:
        # Execute saved query by ID
        query = db.query(Query).filter(Query.id == execute_data.query_id).first()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        datasource = db.query(DataSource).filter(DataSource.id == query.datasource_id).first()
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        sql_to_execute = query.sql_query
    else:
        # Execute ad-hoc query
        datasource = db.query(DataSource).filter(DataSource.id == execute_data.datasource_id).first()
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        sql_to_execute = execute_data.sql_query
    
    # Initialize cache service
    cache_service = CacheService()
    
    # Try to get cached result
    cached_result = cache_service.get_cached_result(
        datasource.id,
        sql_to_execute,
        execute_data.limit
    )
    
    if cached_result:
        # Return cached result
        return QueryResult(
            columns=cached_result["columns"],
            rows=cached_result["rows"],
            total_rows=cached_result.get("total_rows", len(cached_result["rows"])),
            execution_time=cached_result.get("execution_time", 0),
            from_cache=True,
            cached_at=cached_result.get("cached_at")
        )
    
    # Execute query if not cached
    service = QueryService()
    start_time = time.time()
    
    try:
        result = await service.execute_query(
            datasource.type,
            datasource.connection_config,
            sql_to_execute,
            limit=execute_data.limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query execution failed: {str(e)}"
        )
    
    execution_time = time.time() - start_time
    
    # Prepare result
    query_result = {
        "columns": result["columns"],
        "rows": result["rows"],
        "total_rows": len(result["rows"]),
        "execution_time": execution_time
    }
    
    # Cache the result (15 minutes TTL)
    cache_service.set_cached_result(
        datasource.id,
        sql_to_execute,
        query_result,
        limit=execute_data.limit,
        ttl=900  # 15 minutes
    )
    
    return QueryResult(
        columns=query_result["columns"],
        rows=query_result["rows"],
        total_rows=query_result["total_rows"],
        execution_time=query_result["execution_time"],
        from_cache=False
    )

@router.put("/{query_id}", response_model=QueryResponse)
async def update_query(
    query_id: str,
    query_data: QueryUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Update fields
    if query_data.name is not None:
        query.name = query_data.name
    if query_data.description is not None:
        query.description = query_data.description
    if query_data.datasource_id is not None:
        query.datasource_id = query_data.datasource_id
    if query_data.query_type is not None:
        query.query_type = query_data.query_type
    if query_data.query_config is not None:
        query.query_config = query_data.query_config
    if query_data.sql_query is not None:
        query.sql_query = query_data.sql_query
    
    db.commit()
    db.refresh(query)
    
    return QueryResponse.from_orm(query)

@router.delete("/{query_id}")
async def delete_query(
    query_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Query).filter(Query.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    db.delete(query)
    db.commit()
    return {"message": "Query deleted successfully"}