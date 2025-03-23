from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from events import service

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/{short_code}", description="События ссылки (создание/обновление/удаление)")
async def redirectShorter(
    short_code: Annotated[str, "Короткий код ссылки"],
    session: AsyncSession = Depends(get_async_session)
):
    return await service.get_shorturl_events(short_code, session)
