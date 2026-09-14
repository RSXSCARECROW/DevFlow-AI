from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import engine, Base, SessionLocal
import models

from auth import router as auth_router
from auth import get_current_user
from ai_service import (
    analyze_project as analyze_project_service,
    generate_project_plan,
    copilot_answer,
)


# =========================
# DATABASE
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="DevFlow AI",
    description="AI-powered project management platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


# =========================
# PYDANTIC SCHEMAS
# =========================

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TaskCreate(BaseModel):
    title: str
    description: str | None = None

    status: Literal[
        "Todo",
        "In Progress",
        "Completed"
    ] = "Todo"

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ] = "Medium"

    due_date: datetime | None = None
    project_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    status: Literal[
        "Todo",
        "In Progress",
        "Completed"
    ] | None = None

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ] | None = None

    due_date: datetime | None = None


# =========================
# HELPER FUNCTIONS
# =========================

def get_owned_project(
    db,
    project_id: int,
    user_id: int
):
    project = (
        db.query(models.Project)
        .filter(
            models.Project.id == project_id,
            models.Project.owner_id == user_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


def get_owned_task(
    db,
    task_id: int,
    user_id: int
):
    task = (
        db.query(models.Task)
        .join(
            models.Project,
            models.Task.project_id == models.Project.id
        )
        .filter(
            models.Task.id == task_id,
            models.Project.owner_id == user_id
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# =========================
# BASIC ROUTES
# =========================

@app.get("/")
def home():
    return {
        "message": "Welcome to DevFlow AI!"
    }


@app.get("/hello")
def hello():
    return {
        "message": "Hello"
    }


@app.get("/about")
def about():
    return {
        "message": (
            "DevFlow AI is an AI-powered "
            "project management platform"
        )
    }


# =========================
# PROJECT ROUTES
# =========================

@app.post("/projects")
def create_project(
    project: ProjectCreate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        new_project = models.Project(
            name=project.name,
            description=project.description,
            owner_id=current_user.id
        )

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return {
            "message": "Project created successfully",
            "project": {
                "id": new_project.id,
                "name": new_project.name,
                "description": new_project.description,
                "owner_id": new_project.owner_id
            }
        }

    finally:
        db.close()


@app.get("/projects")
def get_projects(
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        projects = (
            db.query(models.Project)
            .filter(
                models.Project.owner_id == current_user.id
            )
            .all()
        )

        return [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "owner_id": project.owner_id
            }
            for project in projects
        ]

    finally:
        db.close()


@app.get("/projects/{project_id}")
def get_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id
        }

    finally:
        db.close()


@app.put("/projects/{project_id}")
def update_project(
    project_id: int,
    updated_project: ProjectUpdate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        if updated_project.name is not None:
            project.name = updated_project.name

        if updated_project.description is not None:
            project.description = updated_project.description

        db.commit()
        db.refresh(project)

        return {
            "message": "Project updated successfully",
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "owner_id": project.owner_id
            }
        }

    finally:
        db.close()


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        db.delete(project)
        db.commit()

        return {
            "message": "Project deleted successfully"
        }

    finally:
        db.close()


# =========================
# AI PROJECT ANALYSIS
# =========================

@app.post("/projects/{project_id}/analyze")
def analyze_project_with_ai(
    project_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        analysis = analyze_project_service(
            project.name,
            project.description or ""
        )

        return {
            "project_id": project.id,
            "project_name": project.name,
            "ai_analysis": analysis
        }

    finally:
        db.close()


# =========================
# TASK ROUTES
# =========================

@app.post("/tasks")
def create_task(
    task: TaskCreate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            task.project_id,
            current_user.id
        )

        new_task = models.Task(
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            project_id=project.id
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return {
            "message": "Task created successfully",
            "task": {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "status": new_task.status,
                "priority": new_task.priority,
                "due_date": new_task.due_date,
                "created_at": new_task.created_at,
                "updated_at": new_task.updated_at,
                "project_id": new_task.project_id
            }
        }

    finally:
        db.close()


@app.get("/tasks")
def get_tasks(
    status: str | None = Query(
        default=None,
        description="Filter by task status"
    ),
    priority: str | None = Query(
        default=None,
        description="Filter by task priority"
    ),
    project_id: int | None = Query(
        default=None,
        description="Filter by project ID"
    ),
    search: str | None = Query(
        default=None,
        description="Search task title or description"
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of tasks to skip"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of tasks to return"
    ),
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        query = (
            db.query(models.Task)
            .join(
                models.Project,
                models.Task.project_id == models.Project.id
            )
            .filter(
                models.Project.owner_id == current_user.id
            )
        )

        if status:
            query = query.filter(
                models.Task.status == status
            )

        if priority:
            query = query.filter(
                models.Task.priority == priority
            )

        if project_id is not None:
            query = query.filter(
                models.Task.project_id == project_id
            )

        if search:
            search_pattern = f"%{search}%"

            query = query.filter(
                (models.Task.title.ilike(search_pattern))
                |
                (models.Task.description.ilike(search_pattern))
            )

        total = query.count()

        tasks = (
            query
            .order_by(models.Task.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                    "project_id": task.project_id
                }
                for task in tasks
            ]
        }

    finally:
        db.close()


@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        task = get_owned_task(
            db,
            task_id,
            current_user.id
        )

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "project_id": task.project_id
        }

    finally:
        db.close()


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    updated_task: TaskUpdate,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        task = get_owned_task(
            db,
            task_id,
            current_user.id
        )

        if updated_task.title is not None:
            task.title = updated_task.title

        if updated_task.description is not None:
            task.description = updated_task.description

        if updated_task.status is not None:
            task.status = updated_task.status

        if updated_task.priority is not None:
            task.priority = updated_task.priority

        if updated_task.due_date is not None:
            task.due_date = updated_task.due_date

        db.commit()
        db.refresh(task)

        return {
            "message": "Task updated successfully",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "project_id": task.project_id
            }
        }

    finally:
        db.close()


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        task = get_owned_task(
            db,
            task_id,
            current_user.id
        )

        db.delete(task)
        db.commit()

        return {
            "message": "Task deleted successfully"
        }

    finally:
        db.close()


# =========================
# GET PROJECT TASKS
# =========================

@app.get("/projects/{project_id}/tasks")
def get_project_tasks(
    project_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        tasks = (
            db.query(models.Task)
            .filter(
                models.Task.project_id == project_id
            )
            .all()
        )

        return {
            "project_id": project.id,
            "project_name": project.name,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at
                }
                for task in tasks
            ]
        }

    finally:
        db.close()


# =========================
# PROJECT PROGRESS
# =========================

@app.get("/projects/{project_id}/progress")
def get_project_progress(
    project_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        tasks = (
            db.query(models.Task)
            .filter(
                models.Task.project_id == project_id
            )
            .all()
        )

        total_tasks = len(tasks)

        completed_tasks = [
            task
            for task in tasks
            if task.status.lower() == "completed"
        ]

        completed_count = len(completed_tasks)

        if total_tasks == 0:
            progress_percentage = 0
        else:
            progress_percentage = round(
                (completed_count / total_tasks) * 100
            )

        return {
            "project_id": project.id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "progress_percentage": progress_percentage
        }

    finally:
        db.close()


# =========================
# PROJECT DASHBOARD
# =========================

@app.get("/projects/{project_id}/dashboard")
def get_project_dashboard(
    project_id: int,
    current_user: models.User = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        project = get_owned_project(
            db,
            project_id,
            current_user.id
        )

        tasks = (
            db.query(models.Task)
            .filter(
                models.Task.project_id == project_id
            )
            .order_by(
                models.Task.created_at.desc()
            )
            .all()
        )

        now = datetime.utcnow()

        total_tasks = len(tasks)

        completed_tasks = [
            task
            for task in tasks
            if task.status == "Completed"
        ]

        in_progress_tasks = [
            task
            for task in tasks
            if task.status == "In Progress"
        ]

        todo_tasks = [
            task
            for task in tasks
            if task.status == "Todo"
        ]

        overdue_tasks = [
            task
            for task in tasks
            if (
                task.due_date is not None
                and task.due_date < now
                and task.status != "Completed"
            )
        ]

        upcoming_tasks = [
            task
            for task in tasks
            if (
                task.due_date is not None
                and task.due_date >= now
                and task.status != "Completed"
            )
        ]

        critical_tasks = [
            task
            for task in tasks
            if task.priority == "Critical"
        ]

        high_priority_tasks = [
            task
            for task in tasks
            if task.priority == "High"
        ]

        if total_tasks == 0:
            completion_percentage = 0
        else:
            completion_percentage = round(
                (len(completed_tasks) / total_tasks) * 100
            )

        tasks_by_status = {
            "Todo": len(todo_tasks),
            "In Progress": len(in_progress_tasks),
            "Completed": len(completed_tasks)
        }

        tasks_by_priority = {
            "Low": len([
                task
                for task in tasks
                if task.priority == "Low"
            ]),
            "Medium": len([
                task
                for task in tasks
                if task.priority == "Medium"
            ]),
            "High": len(high_priority_tasks),
            "Critical": len(critical_tasks)
        }

        recent_tasks = [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
                "created_at": task.created_at
            }
            for task in tasks[:5]
        ]

        return {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "owner_id": project.owner_id
            },
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": len(completed_tasks),
                "in_progress_tasks": len(in_progress_tasks),
                "todo_tasks": len(todo_tasks),
                "overdue_tasks": len(overdue_tasks),
                "upcoming_tasks": len(upcoming_tasks),
                "critical_tasks": len(critical_tasks),
                "high_priority_tasks": len(high_priority_tasks),
                "completion_percentage": completion_percentage
            },
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
            "recent_tasks": recent_tasks
        }

    finally:
        db.close()

# =========================
# PHASE 2 — AI ENGINEER FEATURES
# =========================

class GeneratePlanRequest(BaseModel):
    project_idea: str = Field(..., min_length=10, max_length=5000)


class PlanTask(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: Literal["Low", "Medium", "High", "Critical"] = "Medium"
    estimated_hours: float = Field(default=1, ge=0, le=1000)
    dependencies: list[str] = Field(default_factory=list)


class GeneratedPlan(BaseModel):
    project_title: str
    summary: str
    goals: list[str] = Field(default_factory=list)
    tasks: list[PlanTask] = Field(default_factory=list, min_length=1, max_length=20)
    risks: list[str] = Field(default_factory=list)
    recommended_order: list[str] = Field(default_factory=list)


class ApplyPlanRequest(BaseModel):
    project_id: int
    plan: GeneratedPlan


class CopilotRequest(BaseModel):
    project_id: int
    question: str = Field(..., min_length=3, max_length=2000)


def _project_context(project, tasks):
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
        },
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date,
            }
            for task in tasks
        ],
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "devflow-ai"}


@app.post("/ai/generate-plan", response_model=GeneratedPlan, tags=["AI Engineer Features"])
def generate_plan(
    request: GeneratePlanRequest,
    current_user: models.User = Depends(get_current_user),
):
    try:
        result = generate_project_plan(request.project_idea)
        return GeneratedPlan.model_validate(result)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI plan generation failed: {exc}")


@app.post("/ai/apply-plan", tags=["AI Engineer Features"])
def apply_plan(
    request: ApplyPlanRequest,
    current_user: models.User = Depends(get_current_user),
):
    db = SessionLocal()
    try:
        project = get_owned_project(db, request.project_id, current_user.id)
        created_tasks = []
        for plan_task in request.plan.tasks:
            task = models.Task(
                title=plan_task.title,
                description=plan_task.description,
                priority=plan_task.priority,
                status="Todo",
                project_id=project.id,
            )
            db.add(task)
            created_tasks.append(task)
        db.commit()
        for task in created_tasks:
            db.refresh(task)
        return {
            "message": "Approved AI plan applied successfully",
            "project_id": project.id,
            "created_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "status": task.status,
                    "project_id": task.project_id,
                }
                for task in created_tasks
            ],
        }
    finally:
        db.close()


@app.post("/ai/copilot", tags=["AI Engineer Features"])
def project_copilot(
    request: CopilotRequest,
    current_user: models.User = Depends(get_current_user),
):
    db = SessionLocal()
    try:
        project = get_owned_project(db, request.project_id, current_user.id)
        tasks = db.query(models.Task).filter(models.Task.project_id == project.id).all()
        context = _project_context(project, tasks)
        try:
            result = copilot_answer(context, request.question)
            return {"project_id": project.id, "question": request.question, "copilot": result}
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"AI copilot failed: {exc}")
    finally:
        db.close()
