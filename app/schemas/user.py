from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128
    )
    

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)
    
class UpdateUser(BaseModel):
    name: str | None = None,
    email: EmailStr | None = None
    
