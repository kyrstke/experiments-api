import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db

SQLITE_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def experiment_payload():
    """Generate an experiment payload."""
    return {
        "description": "Experiment A",
        "sample_ratio": 0.5,
        "teams": [
            {"name": "Team A"},
            {"name": "Team B"},
        ],
    }


@pytest.fixture()
def experiment_payload_updated():
    """Generate an updated experiment payload."""
    return {
        "description": "Experiment A (edited)",
        "sample_ratio": 0.2,
        "teams": [
            {"name": "Team A"},
            {"name": "Team C"},
        ],
    }


@pytest.fixture()
def team_payload():
    """Generate a team payload."""
    return {"name": "Team A"}


@pytest.fixture()
def team_payload_updated():
    """Generate an updated team payload."""
    return {"name": "Team A (edited)"}


@pytest.fixture()
def team_payload_child():
    """Generate a child team payload."""
    return {"name": "Team B", "parent_id": 1}


@pytest.fixture()
def team_payload_descendant():
    """Generate a descendant team payload."""
    return {"name": "Team C", "parent_id": 2}
