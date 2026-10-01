from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, UpdateUser

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

@router.get("/",response_model= list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users

@router.post("/", response_model= UserResponse, status_code= status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    user = User(
        name=payload.name,
        email=payload.email,
    )
    db.add(user)
    
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Email Already Exists"
        )    
    
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def user_user(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "User Not Found"
        )
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UpdateUser, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="The User you are trying to update is not present"
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for field,value in update_data.items():
        setattr(user,field,value)
        
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already user"
        )
    return user

@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db:AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Does not exist"
        )
    
    await db.delete(user)
    
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted because related records exist",
        )
        