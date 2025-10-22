from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.datasource import DataSource
from ...schemas.datasource import (
    DataSourceCreate,
    DataSourceResponse,
    DataSourceTest,
    SchemaResponse
)
from ...services.datasource_service import DataSourceService

router = APIRouter()

@router.post("/", response_model=DataSourceResponse)
async def create_datasource(
    datasource_data: DataSourceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Test connection first
    service = DataSourceService()
    connection_valid = await service.test_connection(datasource_data.type, datasource_data.connection_config)
    if not connection_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect to data source"
        )
    
    # Create datasource
    datasource = DataSource(
        name=datasource_data.name,
        type=datasource_data.type,
        connection_config=datasource_data.connection_config,
        created_by=current_user["sub"]
    )
    db.add(datasource)
    db.commit()
    db.refresh(datasource)
    
    return DataSourceResponse.from_orm(datasource)

@router.get("/", response_model=List[DataSourceResponse])
async def list_datasources(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datasources = db.query(DataSource).filter(DataSource.is_active == True).all()
    return [DataSourceResponse.from_orm(ds) for ds in datasources]

@router.get("/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(
    datasource_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datasource = db.query(DataSource).filter(DataSource.id == datasource_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    return DataSourceResponse.from_orm(datasource)

@router.post("/test", response_model=dict)
async def test_datasource_connection(
    test_data: DataSourceTest,
    current_user: dict = Depends(get_current_user)
):
    service = DataSourceService()
    is_valid = await service.test_connection(test_data.type, test_data.connection_config)
    return {"valid": is_valid}

@router.get("/{datasource_id}/schema", response_model=SchemaResponse)
async def get_datasource_schema(
    datasource_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datasource = db.query(DataSource).filter(DataSource.id == datasource_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    service = DataSourceService()
    schema = await service.get_schema(datasource.type, datasource.connection_config)
    return SchemaResponse(tables=schema)

@router.delete("/{datasource_id}")
async def delete_datasource(
    datasource_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    datasource = db.query(DataSource).filter(DataSource.id == datasource_id).first()
    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found"
        )
    
    datasource.is_active = False
    db.commit()
    return {"message": "Data source deleted successfully"}