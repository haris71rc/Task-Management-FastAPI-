from pydantic import BaseModel, ConfigDict

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
    
class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    page: int
    page_size: int
    total: int
    
    
    