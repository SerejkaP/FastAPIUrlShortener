from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import TEvents
from sqlalchemy import desc, select


async def get_shorturl_events(short_name: str, session: AsyncSession):
    try:
        query = select(TEvents).where(TEvents.short_url == short_name).order_by(
            desc(TEvents.datetime)).limit(100)
        result = await session.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(500, str(e))
