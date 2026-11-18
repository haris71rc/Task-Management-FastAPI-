from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DevicePlatform(str, Enum):
    IOS = "IOS"
    ANDROID = "ANDROID"


class DeviceRegisterRequest(BaseModel):
    fcm_token: str = Field(
        min_length=1,
        max_length=512,
    )

    platform: DevicePlatform

    device_name: str | None = Field(
        default=None,
        max_length=255,
    )


class DeviceResponse(BaseModel):
    id: int
    platform: DevicePlatform
    device_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceDeleteResponse(BaseModel):
    message: str