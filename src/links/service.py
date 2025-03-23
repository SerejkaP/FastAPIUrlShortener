from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import TShortUrl, TUser
from sqlalchemy import select


async def get_user_shorturl_by_name(short_name: str, session: AsyncSession, user: TUser) -> (TShortUrl | None):
    try:
        query = select(TShortUrl).where(TShortUrl.short_name ==
                                        short_name and TShortUrl.user_id == user.id)
        result = await session.execute(query)
        return result.scalar()
    except Exception as e:
        raise HTTPException(500, str(e))


async def get_shorturl_by_name(short_name: str, session: AsyncSession) -> (TShortUrl | None):
    try:
        query = select(TShortUrl).where(TShortUrl.short_name == short_name)
        result = await session.execute(query)
        return result.scalar()
    except Exception as e:
        raise HTTPException(500, str(e))


async def get_shorturls_by_original(original_url: str, session: AsyncSession):
    try:
        query = select(TShortUrl.short_name).where(
            TShortUrl.original_url == original_url)
        result = await session.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(500, str(e))


async def get_shorturls_by_user(user: TUser, session: AsyncSession):
    try:
        query = select(TShortUrl.short_name).where(
            TShortUrl.user_id == user.id).limit(100)
        result = await session.execute(query)
        urls_result = result.scalars().all()
        if urls_result is not None:
            return urls_result
        else:
            return None
    except Exception as e:
        raise HTTPException(500, str(e))
