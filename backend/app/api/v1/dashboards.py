from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.dashboard import Dashboard
from ...schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse
)

router = APIRouter()

@router.post("/", response_model=DashboardResponse)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = Dashboard(
        name=dashboard_data.name,
        description=dashboard_data.description,
        layout=dashboard_data.layout,
        widgets=dashboard_data.widgets,
        filters=dashboard_data.filters,
        is_public=dashboard_data.is_public,
        created_by=current_user.id
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    return DashboardResponse.from_orm(dashboard)

@router.get("/", response_model=List[DashboardResponse])
async def list_dashboards(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboards = db.query(Dashboard).all()
    return [DashboardResponse.from_orm(d) for d in dashboards]

@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    return DashboardResponse.from_orm(dashboard)

@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: str,
    dashboard_data: DashboardUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    # Update fields
    if dashboard_data.name is not None:
        dashboard.name = dashboard_data.name
    if dashboard_data.description is not None:
        dashboard.description = dashboard_data.description
    if dashboard_data.layout is not None:
        dashboard.layout = dashboard_data.layout
    if dashboard_data.widgets is not None:
        dashboard.widgets = dashboard_data.widgets
    if dashboard_data.filters is not None:
        dashboard.filters = dashboard_data.filters
    if dashboard_data.is_public is not None:
        dashboard.is_public = dashboard_data.is_public
    
    db.commit()
    db.refresh(dashboard)
    
    return DashboardResponse.from_orm(dashboard)

@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found"
        )
    
    db.delete(dashboard)
    db.commit()
    return {"message": "Dashboard deleted successfully"}