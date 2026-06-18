import os
os.environ["GROQ_API_KEY"] = "gsk_test"
os.environ["FACEBOOK_APP_SECRET"] = "test"
os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"] = "test"
os.environ["FACEBOOK_VERIFY_TOKEN"] = "test_verify"
os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"] = "test"
os.environ["TELEGRAM_BOT_TOKEN"] = "test:bot"
os.environ["TELEGRAM_STAFF_CHAT_ID"] = "-100test"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


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
