import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app, password_hash, _login_attempts
from app.models import Activity, CommunityGroup, Content, Event, User


@pytest.fixture
def api():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        users = []
        for name, role in [("SunlitKoi", "member"), ("BrightKite", "member"), ("HSSModerator", "moderator"), ("CalmOtter", "member")]:
            user = User(username=name, password_hash=password_hash.hash("synthetic-test-password"), role=role)
            db.add(user)
            users.append(user)
        db.flush()
        db.add(Content(title="Example school conversation", body="A synthetic example about preparing questions for a school conversation.", format="Question", topic="School and childcare", stage="Primary school", author_id=users[1].id))
        future = datetime(2099, 10, 10, 10, tzinfo=timezone.utc)
        db.add(Event(title="Example event", description="A synthetic community session.", kind="Webinar", starts_at=future, mode="Online", host="Demo host"))
        db.add(Activity(title="Example walk", description="A synthetic casual morning walk.", kind="Meetup", starts_at=future, location="General public area", organiser_id=users[1].id))
        db.add(CommunityGroup(name="Example group", description="Synthetic group description", audience="Caregivers"))
        db.commit()

    def override():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override
    _login_attempts.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    engine.dispose()


def login(client, name="SunlitKoi"):
    response = client.post("/api/auth/login", json={"username": name, "password": "synthetic-test-password"})
    assert response.status_code == 200, response.text
    return response.json()["csrf_token"]


def headers(csrf):
    return {"X-CSRF-Token": csrf}
