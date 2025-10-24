"""
Pytest configuration and fixtures for backend tests
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.user import User
from server import app

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user"""
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("testpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authentication headers for test user"""
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def test_datasource(db_session, test_user):
    """Create a test data source (SQLite)"""
    from app.models.datasource import DataSource
    import json
    
    datasource = DataSource(
        name="Test SQLite DB",
        type="sqlite",
        config=json.dumps({"database": ":memory:"}),
        user_id=test_user.id
    )
    db_session.add(datasource)
    db_session.commit()
    db_session.refresh(datasource)
    return datasource


@pytest.fixture(scope="function")
def test_query(db_session, test_user, test_datasource):
    """Create a test query"""
    from app.models.query import Query
    
    query = Query(
        name="Test Query",
        description="A test SQL query",
        datasource_id=test_datasource.id,
        query_type="sql",
        sql_query="SELECT 1 as test_column",
        created_by=test_user.email
    )
    db_session.add(query)
    db_session.commit()
    db_session.refresh(query)
    return query
