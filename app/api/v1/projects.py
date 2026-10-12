from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.dependencies import get_current_user, get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
)
from app.services.project import ProjectService

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
)


@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: Literal["created_at", "name", "id"] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProjectService(db)
    return await service.list_projects(
        user_id=current_user.id,
        page=page,
        limit=limit,
        sort=sort,
        order=order,
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.get_project(project_id)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.create_project(
        name=payload.name,
        description=payload.description,
        owner_id=payload.owner_id,
    )
