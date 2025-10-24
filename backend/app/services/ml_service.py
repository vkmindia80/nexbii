"""
Machine Learning Service
Predictive analytics, anomaly detection, clustering, churn prediction
"""
import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, silhouette_score
)
import uuid

from app.models.datasource import DataSource
from app.models.analytics import MLModel
from app.services.datasource_service import DataSourceService
from app.schemas.analytics import (
    PredictiveModelRequest, PredictiveModelResponse,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    ClusteringRequest, ClusteringResponse,
    ChurnPredictionRequest, ChurnPredictionResponse
)


class MLService:
    """Service for machine learning operations"""

    def __init__(self, db: Session):
        self.db = db
        self.datasource_service = DataSourceService(db)
        self.models_dir = "/app/backend/ml_models"
        os.makedirs(self.models_dir, exist_ok=True)

    async def execute_query(self, datasource_id: str, query: str) -> pd.DataFrame:
        """Execute query and return pandas DataFrame"""
        datasource = self.db.query(DataSource).filter(DataSource.id == datasource_id).first()
        if not datasource:
            raise ValueError("Data source not found")
        
        result = await self.datasource_service.execute_query(datasource_id, query)
        return pd.DataFrame(result['data'], columns=result['columns'])

    # ==================== PREDICTIVE MODELS ====================
    async def train_predictive_model(self, request: PredictiveModelRequest, 
                                   user_id: str) -> PredictiveModelResponse:
        """
        Train predictive model (regression or classification)
        """
        # Execute query
        df = await self.execute_query(request.datasource_id, request.query)
        
        # Prepare data
        X = df[request.feature_columns]
        y = df[request.target_column]
        
        # Handle missing values
        X = X.fillna(X.mean() if X.select_dtypes(include=[np.number]).shape[1] > 0 else 0)
        y = y.fillna(y.mean() if pd.api.types.is_numeric_dtype(y) else y.mode()[0])
        
        # Encode categorical variables
        X_encoded = self._encode_features(X)
        
        # Determine if classification or regression
        is_classification = not pd.api.types.is_numeric_dtype(y) or y.nunique() < 20
        
        # Encode target if classification
        if is_classification:
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)
        else:
            y_encoded = y
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y_encoded, test_size=request.test_size, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Select and train model
        if request.model_type == "linear_regression":
            model = LinearRegression()
        elif request.model_type == "logistic_regression":
            model = LogisticRegression(max_iter=1000)
        elif request.model_type == "random_forest":
            if is_classification:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif request.model_type == "decision_tree":
            if is_classification:
                model = DecisionTreeClassifier(random_state=42)
            else:
                model = DecisionTreeRegressor(random_state=42)
        else:
            raise ValueError(f"Unknown model type: {request.model_type}")
        
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        if is_classification:
            accuracy = accuracy_score(y_test, y_pred)
            
            # Handle multi-class vs binary
            average_param = 'binary' if y.nunique() == 2 else 'weighted'
            
            # Get predictions with proper labels
            predictions = []
            for i in range(len(X_test)):
                pred_label = label_encoder.inverse_transform([int(y_pred[i])])[0]
                actual_label = label_encoder.inverse_transform([int(y_test.iloc[i])])[0]
                predictions.append({
                    "prediction": str(pred_label),
                    "actual": str(actual_label),
                    "correct": pred_label == actual_label
                })
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            
            response = PredictiveModelResponse(
                model_id=str(uuid.uuid4()),
                model_type=request.model_type,
                accuracy=float(accuracy),
                predictions=predictions[:100],  # Limit to 100
                confusion_matrix=cm.tolist()
            )
        else:
            # Regression metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            predictions = []
            for i in range(len(X_test)):
                predictions.append({
                    "prediction": float(y_pred[i]),
                    "actual": float(y_test.iloc[i]),
                    "error": float(abs(y_pred[i] - y_test.iloc[i]))
                })
            
            response = PredictiveModelResponse(
                model_id=str(uuid.uuid4()),
                model_type=request.model_type,
                mae=float(mae),
                rmse=float(rmse),
                r2_score=float(r2),
                predictions=predictions[:100]
            )
        
        # Feature importance (if available)
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(request.feature_columns, 
                                        model.feature_importances_.tolist()))
            response.feature_importance = {k: float(v) for k, v in feature_importance.items()}
        elif hasattr(model, 'coef_'):
            coef = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
            feature_importance = dict(zip(request.feature_columns, coef.tolist()))
            response.feature_importance = {k: float(v) for k, v in feature_importance.items()}
        
        # Save model
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_columns': request.feature_columns,
            'is_classification': is_classification
        }
        if is_classification:
            model_data['label_encoder'] = label_encoder
        
        model_path = os.path.join(self.models_dir, f"{response.model_id}.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        # Save model metadata to database
        ml_model = MLModel(
            id=response.model_id,
            name=f"{request.model_type}_model",
            model_type="classification" if is_classification else "regression",
            algorithm=request.model_type,
            file_path=model_path,
            datasource_id=request.datasource_id,
            target_column=request.target_column,
            feature_columns=request.feature_columns,
            accuracy=response.accuracy if is_classification else None,
            r2_score=response.r2_score,
            mae=response.mae,
            rmse=response.rmse,
            training_samples=len(X_train),
            created_by=user_id
        )
        self.db.add(ml_model)
        self.db.commit()
        
        return response

    def _encode_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        X_encoded = X.copy()
        
        for col in X.columns:
            if X[col].dtype == 'object' or X[col].dtype.name == 'category':
                # Use label encoding for simplicity
                le = LabelEncoder()
                X_encoded[col] = le.fit_transform(X[col].astype(str))
        
        return X_encoded

    # ==================== ANOMALY DETECTION ====================
    async def detect_anomalies(self, request: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
        """
        Detect anomalies using various methods
        """
        # Execute query
        df = await self.execute_query(request.datasource_id, request.query)
        
        # Prepare features
        X = df[request.feature_columns]
        X = X.fillna(X.mean())
        X_encoded = self._encode_features(X)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_encoded)
        
        # Select anomaly detection method
        if request.method == "isolation_forest":
            detector = IsolationForest(contamination=request.contamination, random_state=42)
        elif request.method == "local_outlier_factor":
            detector = LocalOutlierFactor(contamination=request.contamination)
        elif request.method == "one_class_svm":
            detector = OneClassSVM(nu=request.contamination)
        else:
            raise ValueError(f"Unknown method: {request.method}")
        
        # Detect anomalies
        if request.method == "local_outlier_factor":
            predictions = detector.fit_predict(X_scaled)
            scores = detector.negative_outlier_factor_
        else:
            predictions = detector.fit_predict(X_scaled)
            scores = detector.score_samples(X_scaled) if hasattr(detector, 'score_samples') else predictions
        
        # Anomalies are labeled as -1
        anomaly_mask = predictions == -1
        anomalies = df[anomaly_mask].copy()
        anomalies['anomaly_score'] = scores[anomaly_mask].tolist()
        
        return AnomalyDetectionResponse(
            anomalies=anomalies.to_dict(orient='records'),
            anomaly_count=int(anomaly_mask.sum()),
            total_records=len(df),
            anomaly_percentage=float(anomaly_mask.sum() / len(df) * 100),
            anomaly_scores=scores.tolist()
        )

    # ==================== CLUSTERING ====================
    async def perform_clustering(self, request: ClusteringRequest) -> ClusteringResponse:
        """
        Perform clustering analysis
        """
        # Execute query
        df = await self.execute_query(request.datasource_id, request.query)
        
        # Prepare features
        X = df[request.feature_columns]
        X = X.fillna(X.mean())
        X_encoded = self._encode_features(X)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_encoded)
        
        # Determine optimal number of clusters if not provided
        if request.n_clusters is None and request.method == "kmeans":
            request.n_clusters = self._find_optimal_clusters(X_scaled)
        
        # Perform clustering
        if request.method == "kmeans":
            clusterer = KMeans(n_clusters=request.n_clusters, random_state=42)
            labels = clusterer.fit_predict(X_scaled)
            centers = clusterer.cluster_centers_.tolist()
        elif request.method == "hierarchical":
            clusterer = AgglomerativeClustering(n_clusters=request.n_clusters or 3)
            labels = clusterer.fit_predict(X_scaled)
            centers = None
        elif request.method == "dbscan":
            clusterer = DBSCAN(eps=0.5, min_samples=5)
            labels = clusterer.fit_predict(X_scaled)
            centers = None
            request.n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        else:
            raise ValueError(f"Unknown method: {request.method}")
        
        # Calculate silhouette score
        if len(set(labels)) > 1 and -1 not in labels:
            sil_score = silhouette_score(X_scaled, labels)
        else:
            sil_score = 0.0
        
        # Prepare results
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = labels
        
        clusters = df_with_clusters.to_dict(orient='records')
        
        # Cluster summary
        cluster_summary = {}
        for cluster_id in set(labels):
            if cluster_id != -1:  # Exclude noise in DBSCAN
                cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
                cluster_summary[f"cluster_{cluster_id}"] = {
                    "size": len(cluster_data),
                    "percentage": float(len(cluster_data) / len(df) * 100)
                }
        
        return ClusteringResponse(
            clusters=clusters,
            cluster_labels=labels.tolist(),
            cluster_centers=centers,
            silhouette_score=float(sil_score),
            n_clusters=request.n_clusters or len(set(labels)),
            summary=cluster_summary
        )

    def _find_optimal_clusters(self, X: np.ndarray, max_k: int = 10) -> int:
        """Find optimal number of clusters using elbow method"""
        inertias = []
        K_range = range(2, min(max_k + 1, len(X)))
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
        
        # Simple elbow detection (look for largest decrease)
        if len(inertias) < 2:
            return 3
        
        decreases = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
        optimal_k = decreases.index(max(decreases)) + 2
        
        return optimal_k

    # ==================== CHURN PREDICTION ====================
    async def predict_churn(self, request: ChurnPredictionRequest, 
                          user_id: str) -> ChurnPredictionResponse:
        """
        Predict customer churn
        """
        # Execute query
        df = await self.execute_query(request.datasource_id, request.query)
        
        # Prepare data
        X = df[request.feature_columns]
        y = df[request.target_column]
        customer_ids = df[request.customer_id_column]
        
        # Handle missing values
        X = X.fillna(X.mean() if X.select_dtypes(include=[np.number]).shape[1] > 0 else 0)
        
        # Encode features
        X_encoded = self._encode_features(X)
        
        # Split data
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X_encoded, y, customer_ids, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model (best for churn prediction)
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # ROC AUC
        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        except:
            roc_auc = 0.5
        
        # Feature importance
        feature_importance = dict(zip(request.feature_columns, 
                                    model.feature_importances_.tolist()))
        feature_importance = {k: float(v) for k, v in 
                            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)}
        
        # Predict on full dataset to identify high-risk customers
        X_full_scaled = scaler.transform(self._encode_features(X))
        churn_proba = model.predict_proba(X_full_scaled)[:, 1]
        
        # High risk customers (top 20% probability)
        high_risk_threshold = np.percentile(churn_proba, 80)
        high_risk_mask = churn_proba >= high_risk_threshold
        
        high_risk_customers = []
        for idx in np.where(high_risk_mask)[0]:
            high_risk_customers.append({
                "customer_id": str(customer_ids.iloc[idx]),
                "churn_probability": float(churn_proba[idx]),
                "features": X.iloc[idx].to_dict()
            })
        
        # Sort by probability
        high_risk_customers = sorted(high_risk_customers, 
                                    key=lambda x: x['churn_probability'], 
                                    reverse=True)[:50]  # Top 50
        
        # All predictions
        predictions = []
        for i in range(len(X_test)):
            predictions.append({
                "customer_id": str(ids_test.iloc[i]),
                "churn_probability": float(y_pred_proba[i]),
                "predicted_churn": bool(y_pred[i]),
                "actual_churn": bool(y_test.iloc[i])
            })
        
        # Save model
        model_id = str(uuid.uuid4())
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_columns': request.feature_columns
        }
        
        model_path = os.path.join(self.models_dir, f"churn_{model_id}.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        return ChurnPredictionResponse(
            model_id=model_id,
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            roc_auc=float(roc_auc),
            feature_importance=feature_importance,
            high_risk_customers=high_risk_customers,
            predictions=predictions[:100]
        )
