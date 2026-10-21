from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    project_id: int
    assigned_to: int | None = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime | None

class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    status: str
    assigned_to: int | None = None

    class Config:
        from_attributes = True
