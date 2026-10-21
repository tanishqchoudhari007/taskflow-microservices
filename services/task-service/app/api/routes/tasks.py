from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.task import Task
from app.models.project import Project
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)
from app.core.security import get_current_user_id


router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"]
)


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    # Find the project and verify that the logged-in user owns it
    project = db.query(Project).filter(
        Project.id == task.project_id,
        Project.owner_id == current_user_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    new_task = Task(
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get(
    "/",
    response_model=list[TaskResponse]
)
def get_tasks(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    tasks = db.query(Task).join(
        Project,
        Task.project_id == Project.id
    ).filter(
        Project.owner_id == current_user_id
    ).all()

    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    task = db.query(Task).join(
        Project,
        Task.project_id == Project.id
    ).filter(
        Task.id == task_id,
        Project.owner_id == current_user_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    task = db.query(Task).join(
        Project,
        Task.project_id == Project.id
    ).filter(
        Task.id == task_id,
        Project.owner_id == current_user_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status
    task.assigned_to = task_data.assigned_to

    db.commit()
    db.refresh(task)

    return task


@router.delete(
    "/{task_id}"
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    task = db.query(Task).join(
        Project,
        Task.project_id == Project.id
    ).filter(
        Task.id == task_id,
        Project.owner_id == current_user_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }