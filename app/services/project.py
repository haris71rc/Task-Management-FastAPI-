import json
import uuid
from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.cache import get_cache_version, invalidate_project_list
from app.core.redis import redis_client
from app.db.models.project import Project
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.project import ProjectListResponse, ProjectResponse
from app.db.models.outbox_event import OutboxEvent


class ProjectService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.user_repository = UserRepository(db)

    async def list_projects(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        sort: str = "created_at",
        order: str = "desc",
    ) -> ProjectListResponse:
        version = await get_cache_version(user_id)

        cache_key = None

        if version is not None:
            cache_key = (
                f"projects:v1:user:{user_id}:version:{version}"
                f":page:{page}:limit:{limit}"
                f":sort:{sort}:order:{order}"
            )

            try:
                cached_data = await redis_client.get(cache_key)

                if cached_data is not None:
                    return ProjectListResponse.model_validate(
                        json.loads(cached_data)
                    )

            except (RedisError, ValueError):
                # Redis failure or invalid cached JSON:
                # fall back to PostgreSQL.
                pass

        # Cache miss or Redis unavailable.
        projects = await self.project_repository.list_for_user(
            user_id=user_id,
            page=page,
            limit=limit,
            sort=sort,
            order=order,
        )
        total = await self.project_repository.count_for_user(user_id)

        response = ProjectListResponse(
            items=[
                ProjectResponse.model_validate(project)
                for project in projects
            ],
            page=page,
            page_size=limit,
            total=total,
        )

        # Best-effort cache write. The API should still work
        # if Redis becomes unavailable.
        if cache_key is not None:
            try:
                await redis_client.set(
                    cache_key,
                    json.dumps(response.model_dump(mode="json")),
                    ex=60,
                )
            except RedisError:
                pass

        return response

    async def get_project(self, project_id: int) -> Project:
        project = await self.project_repository.get_detail(project_id)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return project

    async def create_project(
        self,
        name: str,
        description: str | None,
        owner_id: int,
    ) -> Project:
        user = await self.user_repository.get_by_id(owner_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found",
            )

        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )

        try:
            await self.project_repository.create(project)
            
            await self.db.flush()
            
            event = OutboxEvent(
                id= uuid.uuid4,
                event_type= "project.created",
                payload = {
                    "project_id" : project.id,
                    "recipient_email": user.email,
                },
                idempotency_key=f"project-created:{project.id}",
            )
            await self.db.add(event)
            
            await self.db.commit()
            await self.db.refresh(project)
        except Exception:
            await self.db.rollback()
            raise

        try:
            await invalidate_project_list(owner_id)
        except RedisError:
            pass

        return project
