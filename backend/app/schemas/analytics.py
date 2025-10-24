"""
Analytics schemas for advanced analytics features
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


# ============== Cohort Analysis ==============
class CohortAnalysisRequest(BaseModel):
    datasource_id: str
    user_id_column: str
    event_date_column: str
    cohort_date_column: str
    table_name: str
    filters: Optional[Dict[str, Any]] = None
    period_type: Literal["daily", "weekly", "monthly"] = "monthly"


class CohortAnalysisResponse(BaseModel):
    cohort_data: List[Dict[str, Any]]
    cohort_labels: List[str]
    period_labels: List[str]
    retention_matrix: List[List[float]]
    summary: Dict[str, Any]


# ============== Funnel Analysis ==============
class FunnelStage(BaseModel):
    name: str
    condition: str  # SQL WHERE clause


class FunnelAnalysisRequest(BaseModel):
    datasource_id: str
    table_name: str
    user_id_column: str
    timestamp_column: str
    stages: List[FunnelStage]
    time_window_days: Optional[int] = 30


class FunnelAnalysisResponse(BaseModel):
    stages: List[Dict[str, Any]]  # name, count, conversion_rate, drop_off_rate
    total_entered: int
    total_completed: int
    overall_conversion: float
    avg_time_to_complete: Optional[float] = None


# ============== Time Series Forecasting ==============
class TimeSeriesForecastRequest(BaseModel):
    datasource_id: str
    query: str  # SQL query returning date and value columns
    date_column: str
    value_column: str
    periods: int = 30  # Number of periods to forecast
    frequency: Literal["D", "W", "M", "Q", "Y"] = "D"
    model_type: Literal["arima", "prophet", "seasonal"] = "arima"
    confidence_interval: float = 0.95


class TimeSeriesForecastResponse(BaseModel):
    historical_dates: List[str]
    historical_values: List[float]
    forecast_dates: List[str]
    forecast_values: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    model_metrics: Dict[str, Any]
    trend_direction: str  # "increasing", "decreasing", "stable"


# ============== Statistical Tests ==============
class StatisticalTestRequest(BaseModel):
    datasource_id: str
    test_type: Literal["ttest", "chi_square", "anova", "correlation", "normality"]
    query: str  # SQL query returning data
    columns: List[str]
    group_column: Optional[str] = None
    alpha: float = 0.05


class StatisticalTestResponse(BaseModel):
    test_type: str
    statistic: float
    p_value: float
    significant: bool
    conclusion: str
    details: Dict[str, Any]


# ============== Pivot Table ==============
class PivotTableRequest(BaseModel):
    datasource_id: str
    query: str
    rows: List[str]
    columns: List[str]
    values: str
    aggfunc: Literal["sum", "mean", "count", "min", "max", "median", "std"] = "sum"


class PivotTableResponse(BaseModel):
    pivot_data: List[Dict[str, Any]]
    row_labels: List[str]
    column_labels: List[str]
    grand_total: Optional[float] = None


# ============== Data Profiling ==============
class DataProfilingRequest(BaseModel):
    datasource_id: str
    table_name: Optional[str] = None
    query: Optional[str] = None
    sample_size: Optional[int] = 10000


class ColumnProfile(BaseModel):
    column_name: str
    data_type: str
    missing_count: int
    missing_percentage: float
    unique_count: int
    unique_percentage: float
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    quartiles: Optional[Dict[str, float]] = None
    outliers_count: Optional[int] = None
    top_values: Optional[List[Dict[str, Any]]] = None


class DataProfilingResponse(BaseModel):
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    correlation_matrix: Optional[Dict[str, Any]] = None
    data_quality_score: float
    issues: List[str]


# ============== ML Models ==============
class PredictiveModelRequest(BaseModel):
    datasource_id: str
    query: str
    target_column: str
    feature_columns: List[str]
    model_type: Literal["linear_regression", "logistic_regression", "random_forest", "decision_tree"]
    test_size: float = 0.2
    cross_validation: bool = True


class PredictiveModelResponse(BaseModel):
    model_id: str
    model_type: str
    accuracy: Optional[float] = None
    r2_score: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    feature_importance: Optional[Dict[str, float]] = None
    predictions: List[Dict[str, Any]]
    confusion_matrix: Optional[List[List[int]]] = None


class AnomalyDetectionRequest(BaseModel):
    datasource_id: str
    query: str
    feature_columns: List[str]
    method: Literal["isolation_forest", "local_outlier_factor", "one_class_svm"] = "isolation_forest"
    contamination: float = 0.1


class AnomalyDetectionResponse(BaseModel):
    anomalies: List[Dict[str, Any]]
    anomaly_count: int
    total_records: int
    anomaly_percentage: float
    anomaly_scores: List[float]


class ClusteringRequest(BaseModel):
    datasource_id: str
    query: str
    feature_columns: List[str]
    n_clusters: Optional[int] = None  # If None, will auto-determine
    method: Literal["kmeans", "hierarchical", "dbscan"] = "kmeans"


class ClusteringResponse(BaseModel):
    clusters: List[Dict[str, Any]]
    cluster_labels: List[int]
    cluster_centers: Optional[List[List[float]]] = None
    silhouette_score: float
    n_clusters: int
    summary: Dict[str, Any]


class ChurnPredictionRequest(BaseModel):
    datasource_id: str
    query: str
    customer_id_column: str
    target_column: str  # Binary: 0 = not churned, 1 = churned
    feature_columns: List[str]


class ChurnPredictionResponse(BaseModel):
    model_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    feature_importance: Dict[str, float]
    high_risk_customers: List[Dict[str, Any]]
    predictions: List[Dict[str, Any]]


# ============== Saved Analytics ==============
class SavedAnalysis(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    analysis_type: str
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
