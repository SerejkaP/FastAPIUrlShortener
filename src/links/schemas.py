from datetime import datetime
from pydantic import AnyUrl, BaseModel, Field


class ShortUrlParameters(BaseModel):
    original_url: AnyUrl
    custom_alias: str | None = Field(
        min_length=4, description="Короткая ссылка должна быть больше 4 символов!")
    expires_at: datetime | None = None


class UpdateParameters(BaseModel):
    original_url: AnyUrl
    expires_at: datetime | None = None


class ShortUrlStats(BaseModel):
    original_url: AnyUrl
    create_time: datetime
    redirect_count: int
    last_redirect: datetime | None
