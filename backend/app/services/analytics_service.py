"""
Advanced Analytics Service
Provides cohort analysis, funnel analysis, time series forecasting, statistical tests, pivot tables
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    print(f"⚠️  Prophet not available: {e}")
    PROPHET_AVAILABLE = False
import warnings
warnings.filterwarnings('ignore')

from app.models.datasource import DataSource
from app.services.datasource_service import DataSourceService
from app.schemas.analytics import (
    CohortAnalysisRequest, CohortAnalysisResponse,
    FunnelAnalysisRequest, FunnelAnalysisResponse,
    TimeSeriesForecastRequest, TimeSeriesForecastResponse,
    StatisticalTestRequest, StatisticalTestResponse,
    PivotTableRequest, PivotTableResponse
)


class AnalyticsService:
    """Service for advanced analytics operations"""

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

    # ==================== COHORT ANALYSIS ====================
    async def cohort_analysis(self, request: CohortAnalysisRequest) -> CohortAnalysisResponse:
        """
        Perform cohort analysis for user retention tracking
        """
        # Build query
        query = f"""
            SELECT 
                {request.user_id_column} as user_id,
                {request.event_date_column} as event_date,
                {request.cohort_date_column} as cohort_date
            FROM {request.table_name}
        """
        
        if request.filters:
            where_clauses = [f"{k} = '{v}'" for k, v in request.filters.items()]
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Execute query
        df = await self.execute_query(request.datasource_id, query)
        
        # Convert to datetime
        df['event_date'] = pd.to_datetime(df['event_date'])
        df['cohort_date'] = pd.to_datetime(df['cohort_date'])
        
        # Determine cohort based on period type
        if request.period_type == "monthly":
            df['cohort'] = df['cohort_date'].dt.to_period('M')
            df['period'] = df['event_date'].dt.to_period('M')
        elif request.period_type == "weekly":
            df['cohort'] = df['cohort_date'].dt.to_period('W')
            df['period'] = df['event_date'].dt.to_period('W')
        else:  # daily
            df['cohort'] = df['cohort_date'].dt.to_period('D')
            df['period'] = df['event_date'].dt.to_period('D')
        
        # Calculate period number (periods since cohort)
        df['period_number'] = (df['period'] - df['cohort']).apply(lambda x: x.n)
        
        # Create cohort table
        cohort_data = df.groupby(['cohort', 'period_number'])['user_id'].nunique().reset_index()
        cohort_data.rename(columns={'user_id': 'users'}, inplace=True)
        
        # Pivot to create retention matrix
        retention_matrix = cohort_data.pivot(index='cohort', columns='period_number', values='users')
        
        # Calculate retention percentages
        cohort_sizes = retention_matrix.iloc[:, 0]
        retention_percentage = retention_matrix.divide(cohort_sizes, axis=0) * 100
        
        # Prepare response
        cohort_labels = [str(c) for c in retention_matrix.index]
        period_labels = [f"Period {i}" for i in retention_matrix.columns]
        retention_data = retention_percentage.fillna(0).values.tolist()
        
        # Calculate summary statistics
        avg_retention = {}
        for period in retention_percentage.columns:
            avg_retention[f"period_{period}"] = float(retention_percentage[period].mean())
        
        summary = {
            "total_cohorts": len(cohort_labels),
            "average_retention_by_period": avg_retention,
            "best_cohort": cohort_labels[retention_percentage.iloc[:, -1].idxmax()] if len(retention_percentage) > 0 else None,
            "worst_cohort": cohort_labels[retention_percentage.iloc[:, -1].idxmin()] if len(retention_percentage) > 0 else None
        }
        
        return CohortAnalysisResponse(
            cohort_data=cohort_data.to_dict(orient='records'),
            cohort_labels=cohort_labels,
            period_labels=period_labels,
            retention_matrix=retention_data,
            summary=summary
        )

    # ==================== FUNNEL ANALYSIS ====================
    async def funnel_analysis(self, request: FunnelAnalysisRequest) -> FunnelAnalysisResponse:
        """
        Perform funnel analysis for conversion tracking
        """
        stages_data = []
        previous_users = None
        total_entered = 0
        
        for i, stage in enumerate(request.stages):
            # Build query for this stage
            query = f"""
                SELECT DISTINCT {request.user_id_column} as user_id,
                       MIN({request.timestamp_column}) as first_event_time
                FROM {request.table_name}
                WHERE {stage.condition}
            """
            
            if request.time_window_days and i > 0:
                query += f" GROUP BY {request.user_id_column}"
            else:
                query += f" GROUP BY {request.user_id_column}"
            
            df = await self.execute_query(request.datasource_id, query)
            
            if i == 0:
                total_entered = len(df)
                previous_users = set(df['user_id'].tolist())
            else:
                current_users = set(df['user_id'].tolist())
                # Only count users who completed previous stage
                current_users = current_users.intersection(previous_users)
                previous_users = current_users
            
            count = len(previous_users) if i > 0 else total_entered
            conversion_rate = (count / total_entered * 100) if total_entered > 0 else 0
            drop_off = ((stages_data[i-1]['count'] - count) / stages_data[i-1]['count'] * 100) if i > 0 else 0
            
            stages_data.append({
                "name": stage.name,
                "count": count,
                "conversion_rate": round(conversion_rate, 2),
                "drop_off_rate": round(drop_off, 2) if i > 0 else 0
            })
        
        total_completed = stages_data[-1]['count'] if stages_data else 0
        overall_conversion = (total_completed / total_entered * 100) if total_entered > 0 else 0
        
        return FunnelAnalysisResponse(
            stages=stages_data,
            total_entered=total_entered,
            total_completed=total_completed,
            overall_conversion=round(overall_conversion, 2)
        )

    # ==================== TIME SERIES FORECASTING ====================
    async def time_series_forecast(self, request: TimeSeriesForecastRequest) -> TimeSeriesForecastResponse:
        """
        Perform time series forecasting using ARIMA or Prophet
        """
        # Execute query to get time series data
        df = await self.execute_query(request.datasource_id, request.query)
        
        # Prepare data
        df[request.date_column] = pd.to_datetime(df[request.date_column])
        df = df.sort_values(request.date_column)
        df.set_index(request.date_column, inplace=True)
        
        series = df[request.value_column]
        
        # Split historical data
        historical_dates = [d.strftime('%Y-%m-%d') for d in series.index]
        historical_values = series.values.tolist()
        
        # Perform forecasting based on model type
        if request.model_type == "arima":
            forecast_result = self._forecast_arima(series, request.periods, request.confidence_interval)
        elif request.model_type == "prophet":
            forecast_result = self._forecast_prophet(df, request.date_column, request.value_column, 
                                                    request.periods, request.confidence_interval)
        else:  # seasonal
            forecast_result = self._forecast_seasonal(series, request.periods)
        
        # Determine trend
        trend_direction = self._determine_trend(forecast_result['forecast_values'])
        
        return TimeSeriesForecastResponse(
            historical_dates=historical_dates,
            historical_values=historical_values,
            forecast_dates=forecast_result['forecast_dates'],
            forecast_values=forecast_result['forecast_values'],
            lower_bound=forecast_result['lower_bound'],
            upper_bound=forecast_result['upper_bound'],
            model_metrics=forecast_result['metrics'],
            trend_direction=trend_direction
        )

    def _forecast_arima(self, series: pd.Series, periods: int, confidence: float) -> Dict[str, Any]:
        """ARIMA forecasting"""
        try:
            # Fit ARIMA model (auto order selection)
            model = ARIMA(series, order=(1, 1, 1))
            fitted = model.fit()
            
            # Forecast
            forecast = fitted.forecast(steps=periods)
            forecast_df = fitted.get_forecast(steps=periods)
            conf_int = forecast_df.conf_int(alpha=1-confidence)
            
            # Generate future dates
            last_date = series.index[-1]
            freq = pd.infer_freq(series.index) or 'D'
            future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
            
            return {
                'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'forecast_values': forecast.tolist(),
                'lower_bound': conf_int.iloc[:, 0].tolist(),
                'upper_bound': conf_int.iloc[:, 1].tolist(),
                'metrics': {
                    'aic': float(fitted.aic),
                    'bic': float(fitted.bic),
                    'mae': float(np.mean(np.abs(fitted.resid)))
                }
            }
        except Exception as e:
            # Fallback to simple moving average
            return self._forecast_simple_ma(series, periods)

    def _forecast_prophet(self, df: pd.DataFrame, date_col: str, value_col: str, 
                         periods: int, confidence: float) -> Dict[str, Any]:
        """Prophet forecasting"""
        if not PROPHET_AVAILABLE:
            print("⚠️  Prophet not available, falling back to simple moving average")
            return self._forecast_simple_ma(df[value_col], periods)
        
        try:
            # Prepare data for Prophet
            prophet_df = df.reset_index()[[date_col, value_col]]
            prophet_df.columns = ['ds', 'y']
            
            # Fit model
            model = Prophet(interval_width=confidence)
            model.fit(prophet_df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            
            # Extract forecast
            forecast_only = forecast.tail(periods)
            
            return {
                'forecast_dates': forecast_only['ds'].dt.strftime('%Y-%m-%d').tolist(),
                'forecast_values': forecast_only['yhat'].tolist(),
                'lower_bound': forecast_only['yhat_lower'].tolist(),
                'upper_bound': forecast_only['yhat_upper'].tolist(),
                'metrics': {
                    'model': 'Prophet',
                    'seasonality': 'automatic'
                }
            }
        except Exception as e:
            return self._forecast_simple_ma(df[value_col], periods)

    def _forecast_seasonal(self, series: pd.Series, periods: int) -> Dict[str, Any]:
        """Seasonal decomposition forecast"""
        try:
            # Perform seasonal decomposition
            decomposition = seasonal_decompose(series, model='additive', period=min(12, len(series)//2))
            
            # Simple forecast: trend + seasonal
            trend = decomposition.trend.dropna()
            seasonal = decomposition.seasonal.dropna()
            
            # Extend trend linearly
            last_trend = trend.iloc[-1]
            trend_slope = (trend.iloc[-1] - trend.iloc[-2]) if len(trend) > 1 else 0
            
            forecast_values = []
            for i in range(periods):
                trend_value = last_trend + trend_slope * (i + 1)
                seasonal_value = seasonal.iloc[i % len(seasonal)]
                forecast_values.append(trend_value + seasonal_value)
            
            # Generate dates
            last_date = series.index[-1]
            freq = pd.infer_freq(series.index) or 'D'
            future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
            
            # Estimate confidence interval (simple method)
            resid_std = decomposition.resid.std()
            lower_bound = [v - 1.96 * resid_std for v in forecast_values]
            upper_bound = [v + 1.96 * resid_std for v in forecast_values]
            
            return {
                'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'forecast_values': forecast_values,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'metrics': {
                    'model': 'Seasonal Decomposition',
                    'trend_slope': float(trend_slope)
                }
            }
        except Exception:
            return self._forecast_simple_ma(series, periods)

    def _forecast_simple_ma(self, series: pd.Series, periods: int) -> Dict[str, Any]:
        """Simple moving average forecast (fallback)"""
        window = min(7, len(series))
        ma = series.rolling(window=window).mean().iloc[-1]
        
        forecast_values = [ma] * periods
        std = series.std()
        
        last_date = series.index[-1]
        freq = pd.infer_freq(series.index) or 'D'
        future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
        
        return {
            'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'forecast_values': forecast_values,
            'lower_bound': [ma - 1.96 * std] * periods,
            'upper_bound': [ma + 1.96 * std] * periods,
            'metrics': {
                'model': 'Simple Moving Average',
                'window': window
            }
        }

    def _determine_trend(self, forecast_values: List[float]) -> str:
        """Determine if trend is increasing, decreasing, or stable"""
        if len(forecast_values) < 2:
            return "stable"
        
        first_half_avg = np.mean(forecast_values[:len(forecast_values)//2])
        second_half_avg = np.mean(forecast_values[len(forecast_values)//2:])
        
        change_pct = (second_half_avg - first_half_avg) / first_half_avg * 100
        
        if change_pct > 5:
            return "increasing"
        elif change_pct < -5:
            return "decreasing"
        else:
            return "stable"

    # ==================== STATISTICAL TESTS ====================
    async def statistical_test(self, request: StatisticalTestRequest) -> StatisticalTestResponse:
        """
        Perform various statistical tests
        """
        df = await self.execute_query(request.datasource_id, request.query)
        
        if request.test_type == "ttest":
            return self._perform_ttest(df, request)
        elif request.test_type == "chi_square":
            return self._perform_chi_square(df, request)
        elif request.test_type == "anova":
            return self._perform_anova(df, request)
        elif request.test_type == "correlation":
            return self._perform_correlation(df, request)
        elif request.test_type == "normality":
            return self._perform_normality_test(df, request)
        else:
            raise ValueError(f"Unknown test type: {request.test_type}")

    def _perform_ttest(self, df: pd.DataFrame, request: StatisticalTestRequest) -> StatisticalTestResponse:
        """Perform t-test"""
        if len(request.columns) != 2 or not request.group_column:
            raise ValueError("T-test requires 2 groups and a group column")
        
        groups = df[request.group_column].unique()
        if len(groups) != 2:
            raise ValueError("T-test requires exactly 2 groups")
        
        group1 = df[df[request.group_column] == groups[0]][request.columns[0]]
        group2 = df[df[request.group_column] == groups[1]][request.columns[0]]
        
        statistic, p_value = stats.ttest_ind(group1, group2)
        significant = p_value < request.alpha
        
        conclusion = f"The difference between {groups[0]} and {groups[1]} is "
        conclusion += "statistically significant" if significant else "not statistically significant"
        conclusion += f" (p={p_value:.4f}, α={request.alpha})"
        
        return StatisticalTestResponse(
            test_type="Independent t-test",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=significant,
            conclusion=conclusion,
            details={
                "groups": groups.tolist(),
                "group1_mean": float(group1.mean()),
                "group2_mean": float(group2.mean()),
                "group1_std": float(group1.std()),
                "group2_std": float(group2.std())
            }
        )

    def _perform_chi_square(self, df: pd.DataFrame, request: StatisticalTestRequest) -> StatisticalTestResponse:
        """Perform chi-square test"""
        if len(request.columns) != 2:
            raise ValueError("Chi-square test requires exactly 2 categorical columns")
        
        contingency_table = pd.crosstab(df[request.columns[0]], df[request.columns[1]])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        significant = p_value < request.alpha
        
        conclusion = f"The relationship between {request.columns[0]} and {request.columns[1]} is "
        conclusion += "statistically significant" if significant else "not statistically significant"
        conclusion += f" (p={p_value:.4f}, α={request.alpha})"
        
        return StatisticalTestResponse(
            test_type="Chi-Square Test of Independence",
            statistic=float(chi2),
            p_value=float(p_value),
            significant=significant,
            conclusion=conclusion,
            details={
                "degrees_of_freedom": int(dof),
                "contingency_table": contingency_table.to_dict()
            }
        )

    def _perform_anova(self, df: pd.DataFrame, request: StatisticalTestRequest) -> StatisticalTestResponse:
        """Perform ANOVA test"""
        if len(request.columns) != 1 or not request.group_column:
            raise ValueError("ANOVA requires 1 numeric column and a group column")
        
        groups = [df[df[request.group_column] == group][request.columns[0]].values 
                 for group in df[request.group_column].unique()]
        
        statistic, p_value = stats.f_oneway(*groups)
        significant = p_value < request.alpha
        
        conclusion = f"The means across groups in {request.group_column} are "
        conclusion += "significantly different" if significant else "not significantly different"
        conclusion += f" (p={p_value:.4f}, α={request.alpha})"
        
        return StatisticalTestResponse(
            test_type="One-way ANOVA",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=significant,
            conclusion=conclusion,
            details={
                "groups": df[request.group_column].unique().tolist(),
                "group_means": {group: float(df[df[request.group_column] == group][request.columns[0]].mean()) 
                               for group in df[request.group_column].unique()}
            }
        )

    def _perform_correlation(self, df: pd.DataFrame, request: StatisticalTestRequest) -> StatisticalTestResponse:
        """Perform correlation analysis"""
        numeric_cols = df[request.columns].select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            raise ValueError("Correlation requires at least 2 numeric columns")
        
        correlation_matrix = df[numeric_cols].corr()
        
        # Perform significance test for each pair
        significant_pairs = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:
                    corr, p_val = stats.pearsonr(df[col1], df[col2])
                    if p_val < request.alpha:
                        significant_pairs.append({
                            "pair": f"{col1} - {col2}",
                            "correlation": float(corr),
                            "p_value": float(p_val)
                        })
        
        return StatisticalTestResponse(
            test_type="Pearson Correlation",
            statistic=0.0,
            p_value=0.0,
            significant=len(significant_pairs) > 0,
            conclusion=f"Found {len(significant_pairs)} significant correlations",
            details={
                "correlation_matrix": correlation_matrix.to_dict(),
                "significant_correlations": significant_pairs
            }
        )

    def _perform_normality_test(self, df: pd.DataFrame, request: StatisticalTestRequest) -> StatisticalTestResponse:
        """Perform Shapiro-Wilk normality test"""
        if len(request.columns) != 1:
            raise ValueError("Normality test requires exactly 1 numeric column")
        
        data = df[request.columns[0]].dropna()
        
        if len(data) > 5000:
            # Use Kolmogorov-Smirnov for large samples
            statistic, p_value = stats.kstest(data, 'norm')
            test_name = "Kolmogorov-Smirnov"
        else:
            # Use Shapiro-Wilk for smaller samples
            statistic, p_value = stats.shapiro(data)
            test_name = "Shapiro-Wilk"
        
        significant = p_value < request.alpha
        is_normal = not significant
        
        conclusion = f"The data in {request.columns[0]} "
        conclusion += "follows a normal distribution" if is_normal else "does not follow a normal distribution"
        conclusion += f" (p={p_value:.4f}, α={request.alpha})"
        
        return StatisticalTestResponse(
            test_type=f"{test_name} Normality Test",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=significant,
            conclusion=conclusion,
            details={
                "mean": float(data.mean()),
                "std": float(data.std()),
                "skewness": float(stats.skew(data)),
                "kurtosis": float(stats.kurtosis(data))
            }
        )

    # ==================== PIVOT TABLES ====================
    async def pivot_table(self, request: PivotTableRequest) -> PivotTableResponse:
        """
        Create interactive pivot table
        """
        df = await self.execute_query(request.datasource_id, request.query)
        
        # Create pivot table
        pivot = pd.pivot_table(
            df, 
            values=request.values,
            index=request.rows,
            columns=request.columns,
            aggfunc=request.aggfunc,
            fill_value=0
        )
        
        # Convert to dict format
        pivot_dict = pivot.reset_index().to_dict(orient='records')
        
        # Get labels
        row_labels = pivot.index.tolist() if isinstance(pivot.index, pd.Index) else pivot.index.values.tolist()
        column_labels = pivot.columns.tolist() if isinstance(pivot.columns, pd.Index) else pivot.columns.values.tolist()
        
        # Calculate grand total
        grand_total = float(df[request.values].agg(request.aggfunc)) if request.aggfunc != 'count' else len(df)
        
        return PivotTableResponse(
            pivot_data=pivot_dict,
            row_labels=[str(r) for r in row_labels],
            column_labels=[str(c) for c in column_labels],
            grand_total=grand_total
        )
