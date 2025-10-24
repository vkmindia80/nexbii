"""
Analytics API endpoints
Advanced analytics, data profiling, and ML features
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    CohortAnalysisRequest, CohortAnalysisResponse,
    FunnelAnalysisRequest, FunnelAnalysisResponse,
    TimeSeriesForecastRequest, TimeSeriesForecastResponse,
    StatisticalTestRequest, StatisticalTestResponse,
    PivotTableRequest, PivotTableResponse,
    DataProfilingRequest, DataProfilingResponse,
    PredictiveModelRequest, PredictiveModelResponse,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    ClusteringRequest, ClusteringResponse,
    ChurnPredictionRequest, ChurnPredictionResponse
)
from app.services.analytics_service import AnalyticsService
from app.services.data_profiling_service import DataProfilingService
from app.services.ml_service import MLService

router = APIRouter()


# ==================== ADVANCED ANALYTICS ====================

@router.post("/cohort-analysis", response_model=CohortAnalysisResponse)
async def cohort_analysis(
    request: CohortAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform cohort analysis for user retention tracking
    """
    try:
        service = AnalyticsService(db)
        result = await service.cohort_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cohort analysis failed: {str(e)}"
        )


@router.post("/funnel-analysis", response_model=FunnelAnalysisResponse)
async def funnel_analysis(
    request: FunnelAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform funnel analysis for conversion tracking
    """
    try:
        service = AnalyticsService(db)
        result = await service.funnel_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Funnel analysis failed: {str(e)}"
        )


@router.post("/forecast", response_model=TimeSeriesForecastResponse)
async def time_series_forecast(
    request: TimeSeriesForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform time series forecasting
    """
    try:
        service = AnalyticsService(db)
        result = await service.time_series_forecast(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Time series forecasting failed: {str(e)}"
        )


@router.post("/statistical-test", response_model=StatisticalTestResponse)
async def statistical_test(
    request: StatisticalTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform statistical tests (t-test, chi-square, ANOVA, correlation, normality)
    """
    try:
        service = AnalyticsService(db)
        result = await service.statistical_test(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statistical test failed: {str(e)}"
        )


@router.post("/pivot-table", response_model=PivotTableResponse)
async def pivot_table(
    request: PivotTableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create interactive pivot table
    """
    try:
        service = AnalyticsService(db)
        result = await service.pivot_table(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pivot table creation failed: {str(e)}"
        )


# ==================== DATA PROFILING ====================

@router.post("/profile-data", response_model=DataProfilingResponse)
async def profile_data(
    request: DataProfilingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Comprehensive data profiling and quality assessment
    """
    try:
        service = DataProfilingService(db)
        result = await service.profile_data(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data profiling failed: {str(e)}"
        )


@router.get("/column-distribution/{datasource_id}/{table_name}/{column_name}")
async def get_column_distribution(
    datasource_id: str,
    table_name: str,
    column_name: str,
    bins: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get distribution data for a specific column
    """
    try:
        service = DataProfilingService(db)
        result = await service.get_column_distribution(datasource_id, table_name, column_name, bins)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get column distribution: {str(e)}"
        )


@router.get("/detect-correlations/{datasource_id}/{table_name}")
async def detect_correlations(
    datasource_id: str,
    table_name: str,
    threshold: float = 0.7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detect strong correlations between columns
    """
    try:
        service = DataProfilingService(db)
        result = await service.detect_correlations(datasource_id, table_name, threshold)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to detect correlations: {str(e)}"
        )


# ==================== MACHINE LEARNING ====================

@router.post("/predictive-model", response_model=PredictiveModelResponse)
async def train_predictive_model(
    request: PredictiveModelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Train predictive model (regression or classification)
    """
    try:
        service = MLService(db)
        result = await service.train_predictive_model(request, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model training failed: {str(e)}"
        )


@router.post("/anomaly-detection", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detect anomalies using various methods
    """
    try:
        service = MLService(db)
        result = await service.detect_anomalies(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Anomaly detection failed: {str(e)}"
        )


@router.post("/clustering", response_model=ClusteringResponse)
async def perform_clustering(
    request: ClusteringRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform clustering analysis
    """
    try:
        service = MLService(db)
        result = await service.perform_clustering(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Clustering failed: {str(e)}"
        )


@router.post("/churn-prediction", response_model=ChurnPredictionResponse)
async def predict_churn(
    request: ChurnPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict customer churn
    """
    try:
        service = MLService(db)
        result = await service.predict_churn(request, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Churn prediction failed: {str(e)}"
        )


@router.get("/health")
async def analytics_health():
    """Check analytics service health"""
    return {
        "status": "healthy",
        "service": "Analytics & ML",
        "features": [
            "Cohort Analysis",
            "Funnel Analysis",
            "Time Series Forecasting",
            "Statistical Tests",
            "Pivot Tables",
            "Data Profiling",
            "Predictive Models",
            "Anomaly Detection",
            "Clustering",
            "Churn Prediction"
        ]
    }
