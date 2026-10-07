from pydantic import BaseModel, ConfigDict
from app.db.models.task import TaskPriority, TaskStatus

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    owner_id: int
    
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ProjectOwnerResponse(BaseModel):
    id: int
    name:str
    email:str
    
    model_config = ConfigDict(from_attributes=True)

class ProjectTaskResponse(BaseModel):
    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    
    model_config = ConfigDict(from_attributes=True)
    
class ProjectDetailResponse(BaseModel):
    id: int
    name:str
    description:str
    owner: ProjectOwnerResponse
    tasks: list[ProjectTaskResponse]
    
    model_config = ConfigDict(from_attributes=True)

    
class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    page: int
    page_size: int
    total: int
    
class ProjectCreate(BaseModel):
    name: str
    description: str | None
    owner_id: int  
    