"""
Data Profiling Service
Automatic data quality assessment, missing values, outliers, distributions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from scipy import stats

from app.models.datasource import DataSource
from app.services.datasource_service import DataSourceService
from app.schemas.analytics import (
    DataProfilingRequest, DataProfilingResponse, ColumnProfile
)


class DataProfilingService:
    """Service for data quality assessment and profiling"""

    def __init__(self, db: Session):
        self.db = db
        self.datasource_service = DataSourceService(db)

    async def execute_query(self, datasource_id: str, query: str) -> pd.DataFrame:
        """Execute query and return pandas DataFrame"""
        datasource = self.db.query(DataSource).filter(DataSource.id == datasource_id).first()
        if not datasource:
            raise ValueError("Data source not found")
        
        result = await self.datasource_service.execute_query(datasource_id, query)
        return pd.DataFrame(result['data'], columns=result['columns'])

    async def profile_data(self, request: DataProfilingRequest) -> DataProfilingResponse:
        """
        Comprehensive data profiling
        """
        # Build query
        if request.query:
            query = request.query
        elif request.table_name:
            query = f"SELECT * FROM {request.table_name}"
            if request.sample_size:
                query += f" LIMIT {request.sample_size}"
        else:
            raise ValueError("Either query or table_name must be provided")
        
        # Execute query
        df = await self.execute_query(request.datasource_id, query)
        
        # Profile each column
        column_profiles = []
        for col in df.columns:
            profile = self._profile_column(df, col)
            column_profiles.append(profile)
        
        # Calculate correlation matrix for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        correlation_matrix = None
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            correlation_matrix = {
                "columns": numeric_cols,
                "matrix": corr.values.tolist()
            }
        
        # Calculate overall data quality score
        quality_score = self._calculate_quality_score(df, column_profiles)
        
        # Identify issues
        issues = self._identify_issues(df, column_profiles)
        
        return DataProfilingResponse(
            row_count=len(df),
            column_count=len(df.columns),
            columns=column_profiles,
            correlation_matrix=correlation_matrix,
            data_quality_score=quality_score,
            issues=issues
        )

    def _profile_column(self, df: pd.DataFrame, column: str) -> ColumnProfile:
        """Profile a single column"""
        series = df[column]
        
        # Basic stats
        missing_count = int(series.isna().sum())
        missing_percentage = float(missing_count / len(series) * 100)
        unique_count = int(series.nunique())
        unique_percentage = float(unique_count / len(series) * 100)
        
        # Data type
        dtype_str = str(series.dtype)
        
        # Numeric column profiling
        if pd.api.types.is_numeric_dtype(series):
            clean_series = series.dropna()
            
            # Statistical measures
            mean_val = float(clean_series.mean()) if len(clean_series) > 0 else None
            median_val = float(clean_series.median()) if len(clean_series) > 0 else None
            std_val = float(clean_series.std()) if len(clean_series) > 0 else None
            min_val = float(clean_series.min()) if len(clean_series) > 0 else None
            max_val = float(clean_series.max()) if len(clean_series) > 0 else None
            
            # Quartiles
            quartiles = {
                "Q1": float(clean_series.quantile(0.25)) if len(clean_series) > 0 else None,
                "Q2": float(clean_series.quantile(0.50)) if len(clean_series) > 0 else None,
                "Q3": float(clean_series.quantile(0.75)) if len(clean_series) > 0 else None
            }
            
            # Outlier detection (IQR method)
            outliers_count = self._detect_outliers_iqr(clean_series)
            
            # Top values (less relevant for continuous numeric)
            top_values = None
            
        else:
            # Categorical/text column
            mean_val = None
            median_val = None
            std_val = None
            min_val = None
            max_val = None
            quartiles = None
            outliers_count = None
            
            # Top values
            value_counts = series.value_counts().head(10)
            top_values = [
                {"value": str(val), "count": int(count), "percentage": float(count / len(series) * 100)}
                for val, count in value_counts.items()
            ]
        
        return ColumnProfile(
            column_name=column,
            data_type=dtype_str,
            missing_count=missing_count,
            missing_percentage=round(missing_percentage, 2),
            unique_count=unique_count,
            unique_percentage=round(unique_percentage, 2),
            mean=mean_val,
            median=median_val,
            std=std_val,
            min=min_val,
            max=max_val,
            quartiles=quartiles,
            outliers_count=outliers_count,
            top_values=top_values
        )

    def _detect_outliers_iqr(self, series: pd.Series) -> int:
        """Detect outliers using IQR method"""
        if len(series) == 0:
            return 0
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return len(outliers)

    def _calculate_quality_score(self, df: pd.DataFrame, profiles: List[ColumnProfile]) -> float:
        """
        Calculate overall data quality score (0-100)
        Based on: completeness, uniqueness, consistency
        """
        scores = []
        
        # Completeness score (based on missing values)
        total_missing = sum(p.missing_count for p in profiles)
        total_cells = len(df) * len(df.columns)
        completeness = (1 - total_missing / total_cells) * 100 if total_cells > 0 else 0
        scores.append(completeness)
        
        # Uniqueness score (columns with appropriate uniqueness)
        uniqueness_scores = []
        for p in profiles:
            if p.unique_percentage > 0.1:  # At least some variation
                uniqueness_scores.append(min(p.unique_percentage, 100))
        uniqueness = np.mean(uniqueness_scores) if uniqueness_scores else 50
        scores.append(uniqueness)
        
        # Consistency score (based on outliers for numeric columns)
        numeric_profiles = [p for p in profiles if p.outliers_count is not None]
        if numeric_profiles:
            outlier_percentages = [
                (p.outliers_count / (len(df) - p.missing_count) * 100) if (len(df) - p.missing_count) > 0 else 0
                for p in numeric_profiles
            ]
            avg_outlier_pct = np.mean(outlier_percentages)
            consistency = max(0, 100 - avg_outlier_pct * 2)  # Penalize outliers
            scores.append(consistency)
        
        # Overall score
        return round(np.mean(scores), 2)

    def _identify_issues(self, df: pd.DataFrame, profiles: List[ColumnProfile]) -> List[str]:
        """Identify data quality issues"""
        issues = []
        
        # Check for high missing values
        for p in profiles:
            if p.missing_percentage > 50:
                issues.append(f"Column '{p.column_name}' has {p.missing_percentage:.1f}% missing values")
            elif p.missing_percentage > 20:
                issues.append(f"Column '{p.column_name}' has {p.missing_percentage:.1f}% missing values (moderate)")
        
        # Check for low variance
        for p in profiles:
            if p.unique_count == 1 and p.missing_count < len(df):
                issues.append(f"Column '{p.column_name}' has only one unique value (constant)")
        
        # Check for high outlier count
        for p in profiles:
            if p.outliers_count is not None:
                outlier_pct = (p.outliers_count / (len(df) - p.missing_count) * 100) if (len(df) - p.missing_count) > 0 else 0
                if outlier_pct > 10:
                    issues.append(f"Column '{p.column_name}' has {outlier_pct:.1f}% outliers")
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            dup_pct = (duplicate_count / len(df) * 100)
            issues.append(f"{duplicate_count} duplicate rows found ({dup_pct:.1f}%)")
        
        # Check for completely empty columns
        empty_cols = [p.column_name for p in profiles if p.missing_percentage == 100]
        if empty_cols:
            issues.append(f"Completely empty columns: {', '.join(empty_cols)}")
        
        return issues

    async def get_column_distribution(self, datasource_id: str, table_name: str, 
                                     column_name: str, bins: int = 20) -> Dict[str, Any]:
        """Get distribution data for a specific column"""
        query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL"
        df = await self.execute_query(datasource_id, query)
        
        series = df[column_name]
        
        if pd.api.types.is_numeric_dtype(series):
            # Histogram for numeric data
            hist, bin_edges = np.histogram(series, bins=bins)
            
            return {
                "type": "histogram",
                "bins": bin_edges.tolist(),
                "counts": hist.tolist(),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std())
            }
        else:
            # Bar chart for categorical data
            value_counts = series.value_counts().head(20)
            
            return {
                "type": "bar",
                "categories": value_counts.index.tolist(),
                "counts": value_counts.values.tolist()
            }

    async def detect_correlations(self, datasource_id: str, table_name: str, 
                                 threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Detect strong correlations between columns"""
        query = f"SELECT * FROM {table_name} LIMIT 10000"
        df = await self.execute_query(datasource_id, query)
        
        # Get numeric columns only
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return []
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) >= threshold:
                        strong_correlations.append({
                            "column1": col1,
                            "column2": col2,
                            "correlation": float(corr_value),
                            "strength": "strong positive" if corr_value > 0 else "strong negative"
                        })
        
        return strong_correlations
