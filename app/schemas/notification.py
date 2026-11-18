from pydantic import BaseModel, Field


class NotificationTestRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100
    )
    body: str = Field(
        min_length=1,
        max_length=500
    )
    
    data: dict[str,str] | None = None