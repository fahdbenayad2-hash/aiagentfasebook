import os
os.environ["GROQ_API_KEY"] = "gsk_test"
os.environ["FB_APP_SECRET"] = "test"
os.environ["FACEBOOK_APP_SECRET"] = "test"
os.environ["FB_PAGE_ACCESS_TOKEN"] = "test"
os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"] = "test"
os.environ["FB_VERIFY_TOKEN"] = "test_verify"
os.environ["FACEBOOK_VERIFY_TOKEN"] = "test_verify"
os.environ["IG_BUSINESS_ACCOUNT_ID"] = "test"
os.environ["TELEGRAM_BOT_TOKEN"] = "test:bot"
os.environ["TELEGRAM_STAFF_CHAT_ID"] = "-100test"
os.environ["APP_SECRET_KEY"] = "test_secret_key"
os.environ["FEATURE_INTENT_CLASSIFIER"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from app.database import Base, get_db, SessionLocal, engine
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _setup_db():
    """Clean + recreate all tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
