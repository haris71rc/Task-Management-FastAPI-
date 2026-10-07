from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.services.project import ProjectService
from app.db.models.project import Project
from app.dependencies import get_db
from app.schemas.project import ProjectListResponse, ProjectDetailResponse, ProjectResponse, ProjectCreate

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"]
)

@router.get("/",response_model=ProjectListResponse)
async def get_projects(
    page: int= Query(1,ge=1),
    page_size: int = Query(10, ge=1,le=100),
    owner_id: int | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    offset = (page-1) * page_size
    
    stmt = select(Project)
    
    if owner_id is not None:
        stmt = stmt.where(owner_id == Project.owner_id)
    
    if search:
        stmt = stmt.where(Project.name.ilike(f"%{search}%"))
    
    stmt = (
       stmt
        .order_by(
            Project.created_at.desc(),
            Project.id.desc()
        )
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    count_stmt = select(func.count()).select_from(Project)
    
    if owner_id is not None:
        count_stmt = count_stmt.where(Project.owner_id == owner_id)
        
    if search:
        count_stmt = count_stmt.where(Project.name.ilike(f"%{search}%"))
    
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    
    return ProjectListResponse(
        items=projects,
        page=page,
        page_size=page_size,
        total=total
    )
    
@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Project)
        .options(
            joinedload(Project.owner),
            selectinload(Project.tasks)
        )
        .where(Project.id == project_id)
    )
    
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if project is None:
        raise HTTPException(
            status_code= 404,
            detail="Project not found"
        )
    
    return project

@router.post("/", response_model= ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    
    project = await service.create_project(
        name=payload.name,
        description=payload.description,
        owner_id=payload.owner_id
    )
    
    return project
        
    
    
