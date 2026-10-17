from datetime import datetime
from pydantic import ConfigDict,BaseModel

class AttachmentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    task_id: int
    uploaded_by: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)