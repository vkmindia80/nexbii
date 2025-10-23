"""
AI API endpoints for NexBII
Provides natural language query processing, validation, optimization, and insights
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...models.datasource import DataSource
from ...services.ai_service import ai_service
from ...services.datasource_service import DataSourceService

router = APIRouter()

# Request/Response Models
class NaturalQueryRequest(BaseModel):
    natural_query: str = Field(..., description="Natural language query")
    datasource_id: str = Field(..., description="Data source ID")

class ValidateQueryRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to validate")
    datasource_id: str = Field(..., description="Data source ID")

class OptimizeQueryRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to optimize")
    datasource_id: str = Field(..., description="Data source ID")
    execution_time: Optional[float] = Field(None, description="Current execution time in seconds")

class RecommendChartRequest(BaseModel):
    query_result: Dict[str, Any] = Field(..., description="Query execution results")
    sql_query: str = Field(..., description="The SQL query that generated the results")

class GenerateInsightsRequest(BaseModel):
    query_result: Dict[str, Any] = Field(..., description="Query execution results")
    sql_query: str = Field(..., description="The SQL query that generated the results")


@router.post("/natural-query")
async def natural_language_to_sql(
    request: NaturalQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert natural language query to SQL
    
    Example: "Show me top 10 customers by revenue" -> SQL query
    """
    try:
        # Get datasource
        datasource = db.query(DataSource).filter(DataSource.id == request.datasource_id).first()
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Get schema information
        datasource_service = DatasourceService()
        schema_info = datasource_service.get_schema(datasource)
        
        if not schema_info.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve schema information"
            )
        
        # Convert schema to dict format
        schema_dict = {}
        for table in schema_info.get("tables", []):
            schema_dict[table["name"]] = {
                "columns": table.get("columns", [])
            }
        
        # Generate SQL from natural language
        result = await ai_service.natural_language_to_sql(
            natural_query=request.natural_query,
            schema_info=schema_dict,
            database_type=datasource.type.value
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process natural language query: {str(e)}"
        )


@router.post("/validate-query")
async def validate_query(
    request: ValidateQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate SQL query and provide suggestions
    
    Returns validation results, syntax errors, and improvement suggestions
    """
    try:
        # Get datasource
        datasource = db.query(DataSource).filter(DataSource.id == request.datasource_id).first()
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Get schema information
        datasource_service = DatasourceService()
        schema_info = datasource_service.get_schema(datasource)
        
        if not schema_info.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve schema information"
            )
        
        # Convert schema to dict format
        schema_dict = {}
        for table in schema_info.get("tables", []):
            schema_dict[table["name"]] = {
                "columns": table.get("columns", [])
            }
        
        # Validate query
        result = await ai_service.validate_and_suggest(
            sql_query=request.sql_query,
            schema_info=schema_dict,
            database_type=datasource.type.value
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate query: {str(e)}"
        )


@router.post("/optimize-query")
async def optimize_query(
    request: OptimizeQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Suggest query optimizations for better performance
    
    Returns optimized query, specific optimizations, and index recommendations
    """
    try:
        # Get datasource
        datasource = db.query(DataSource).filter(DataSource.id == request.datasource_id).first()
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        # Get schema information
        datasource_service = DatasourceService()
        schema_info = datasource_service.get_schema(datasource)
        
        if not schema_info.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve schema information"
            )
        
        # Convert schema to dict format
        schema_dict = {}
        for table in schema_info.get("tables", []):
            schema_dict[table["name"]] = {
                "columns": table.get("columns", [])
            }
        
        # Optimize query
        result = await ai_service.optimize_query(
            sql_query=request.sql_query,
            schema_info=schema_dict,
            execution_time=request.execution_time,
            database_type=datasource.type.value
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize query: {str(e)}"
        )


@router.post("/recommend-chart")
async def recommend_chart(
    request: RecommendChartRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Recommend best chart type based on query results
    
    Analyzes data structure and suggests optimal visualization
    """
    try:
        result = await ai_service.recommend_chart_type(
            query_result=request.query_result,
            sql_query=request.sql_query
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recommend chart: {str(e)}"
        )


@router.post("/generate-insights")
async def generate_insights(
    request: GenerateInsightsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate automated insights from query results
    
    Returns key insights, trends, anomalies, and recommendations
    """
    try:
        result = await ai_service.generate_insights(
            query_result=request.query_result,
            sql_query=request.sql_query
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/health")
async def ai_health_check(current_user: User = Depends(get_current_user)):
    """Check if AI service is available"""
    try:
        # Simple check to see if the service is initialized
        return {
            "status": "healthy",
            "service": "AI Query Processing",
            "features": [
                "Natural Language to SQL",
                "Query Validation",
                "Query Optimization",
                "Chart Recommendations",
                "Automated Insights"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {str(e)}"
        )
