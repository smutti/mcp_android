from pydantic import BaseModel, Field


class DeviceTarget(BaseModel):
    serial: str | None = Field(default=None, description="Target device serial")


class SelectorInput(BaseModel):
    text: str | None = Field(default=None, description="UI element text")
    resource_id: str | None = Field(default=None, description="UI element resource-id")
    content_desc: str | None = Field(default=None, description="UI element content description")
