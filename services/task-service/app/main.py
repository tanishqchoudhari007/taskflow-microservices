from fastapi import FastAPI
from sqlalchemy import text

from sqlalchemy.orm import Session

from app.database.connection import engine
from app.api.routes.projects import router as projects_router

from app.api.routes.tasks import router as tasks_router


app = FastAPI(title="TaskFlow Task Service")
app.include_router(projects_router)
app.include_router(tasks_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "task-service"
    }


@app.get("/db-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        return {
            "database": result.scalar()
        }