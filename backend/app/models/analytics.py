"""
Analytics model for storing saved analyses and ML models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class SavedAnalysis(Base):
    """Saved analytics configurations"""
    __tablename__ = "saved_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    analysis_type = Column(String(50), nullable=False)  # cohort, funnel, forecast, etc.
    configuration = Column(JSON, nullable=False)
    datasource_id = Column(String, ForeignKey('datasources.id'), nullable=False)
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    datasource = relationship("DataSource", back_populates="analyses")
    user = relationship("User", back_populates="analyses")


class MLModel(Base):
    """Stored ML models and metadata"""
    __tablename__ = "ml_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # regression, classification, clustering
    algorithm = Column(String(50), nullable=False)  # random_forest, kmeans, etc.
    file_path = Column(String(500), nullable=False)  # Path to pickle file
    datasource_id = Column(String, ForeignKey('datasources.id'), nullable=False)
    
    # Model metadata
    target_column = Column(String(100), nullable=True)
    feature_columns = Column(JSON, nullable=False)
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    silhouette_score = Column(Float, nullable=True)
    
    # Training info
    training_samples = Column(Integer, nullable=True)
    training_date = Column(DateTime(timezone=True), server_default=func.now())
    
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    datasource = relationship("DataSource")
    user = relationship("User")
