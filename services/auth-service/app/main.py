from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.routes.auth import router as auth_router


app = FastAPI(title="TaskFlow Auth Service")

app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "auth-service"
    }


@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    return {
        "status": "database session created successfully"
    }