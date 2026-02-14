from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    serial: str = Field(description="ADB serial number")
    state: str = Field(description="ADB connection state")
    model: str | None = Field(default=None, description="Device model if available")
    android_version: str | None = Field(default=None, description="Android version if available")
