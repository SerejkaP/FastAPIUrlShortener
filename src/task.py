import asyncio
from datetime import datetime, timedelta
from database import async_session_maker
from models import EventType, TShortUrl, TEvents
from sqlalchemy import select


async def delete_expired_links():
    while True:
        async with async_session_maker() as session:
            # Ссылки, у которых истек срок действия
            query = select(TShortUrl).where(
                TShortUrl.expires_at < datetime.utcnow())
            result = await session.execute(query)
            expired_links = result.scalars().all()
            for link in expired_links:
                event = TEvents(
                    short_url=link.short_name,
                    event_type=EventType.ShortIsExpired,
                    datetime=datetime.utcnow(),
                    description=f"{link.short_name} удален по истечении времени"
                )
                session.add(event)
                await session.delete(link)
            await session.commit()
        # Запуск таски раз в минуту
        await asyncio.sleep(60)


async def delete_old_links():
    while True:
        async with async_session_maker() as session:
            # Ссылки, которые давно не используются
            query = select(TShortUrl).where(
                (TShortUrl.last_redirect + timedelta(days=120)) < datetime.utcnow())
            result = await session.execute(query)
            old_links = result.scalars().all()
            for link in old_links:
                event = TEvents(
                    short_url=link.short_name,
                    event_type=EventType.ShortIsNotUsed,
                    datetime=datetime.utcnow(),
                    description=f"{link.short_name} не использовался и был удален"
                )
                session.add(event)
                await session.delete(link)
            await session.commit()
        # Запуск таски раз в сутки
        await asyncio.sleep(60*60*24)
