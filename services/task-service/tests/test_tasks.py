
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import Base, get_db
from app.core.security import get_current_user_id

# Import models so SQLAlchemy registers their tables
from app.models.project import Project
from app.models.task import Task


# Create an isolated in-memory SQLite database
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = lambda: 1

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def create_project(client):
    return client.post(
        "/api/projects/",
        json={
            "name": "Test Project",
            "description": "Project created during testing"
        }
    )


def create_task(client, project_id):
    return client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "Task created during testing",
            "project_id": project_id,
            "assigned_to": 1
        }
    )


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_project(client):
    response = create_project(client)

    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"
    assert response.json()["owner_id"] == 1


def test_get_projects(client):
    create_project(client)

    response = client.get("/api/projects/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_project(client):
    project = create_project(client).json()

    response = client.put(
        f"/api/projects/{project['id']}",
        json={
            "name": "Updated Project",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"


def test_delete_project(client):
    project = create_project(client).json()

    response = client.delete(
        f"/api/projects/{project['id']}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"


def test_project_not_found(client):
    response = client.get("/api/projects/999")

    assert response.status_code == 404


def test_create_task(client):
    project = create_project(client).json()

    response = create_task(client, project["id"])

    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
    assert response.json()["project_id"] == project["id"]


def test_create_task_with_invalid_project(client):
    response = create_task(client, 999)

    assert response.status_code == 404


def test_get_tasks(client):
    project = create_project(client).json()
    create_task(client, project["id"])

    response = client.get("/api/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_task(client):
    project = create_project(client).json()
    task = create_task(client, project["id"]).json()

    response = client.put(
        f"/api/tasks/{task['id']}",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "status": "IN_PROGRESS",
            "assigned_to": 2
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["status"] == "IN_PROGRESS"


def test_delete_task(client):
    project = create_project(client).json()
    task = create_task(client, project["id"]).json()

    response = client.delete(
        f"/api/tasks/{task['id']}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"


def test_task_not_found(client):
    response = client.get("/api/tasks/999")

    assert response.status_code == 404


def test_user_cannot_access_another_users_project(client):
    project = create_project(client).json()

    app.dependency_overrides[get_current_user_id] = lambda: 2

    response = client.get(
        f"/api/projects/{project['id']}"
    )

    assert response.status_code == 404
