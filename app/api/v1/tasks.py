from fastapi import APIRouter,status,Depends
from app.schemas.tasks import TaskCreate, TaskResponse
from app.dependencies import get_request_id

router = APIRouter()


@router.get("/{task_id}", response_model= TaskResponse)
async def get_task(task_id: int, request_id: str | None = Depends(get_request_id)):
    return {
        "id": task_id,
        "title": "Learn FastAPI",
        "description": "Build a production backend",
        "request_id": request_id
    }
    
@router.post("",response_model=TaskResponse,status_code= status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    return {
        "id": "1",
        "title": task.title,
        "description": task.description 
    }