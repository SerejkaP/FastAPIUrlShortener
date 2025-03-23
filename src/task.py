import asyncio
from datetime import datetime, timedelta
from database import async_session_maker
from models import EventType, TShortUrl, TEvents
from sqlalchemy import select
from redis_client import get_redis


async def delete_expired_links():
    while True:
        redis_client = await get_redis()
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
                await redis_client.delete(link.short_name, f"{link.short_name}:redirect_count", f"{link.short_name}:last_redirect")
            await session.commit()
        # Запуск таски раз в минуту
        await asyncio.sleep(60)


async def delete_old_links():
    while True:
        redis_client = await get_redis()
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
                await redis_client.delete(link.short_name, f"{link.short_name}:redirect_count", f"{link.short_name}:last_redirect")
            await session.commit()
        # Запуск таски раз в сутки
        await asyncio.sleep(60*60*24)


async def sync_clicks_to_db():
    while True:
        redis_client = await get_redis()
        async with async_session_maker() as session:
            keys = await redis_client.keys("*:redirect_count")
            for key in keys:
                short_code = key.split(":")[0]
                redirect_count = int(await redis_client.get(key) or 0)
                last_redirect = await redis_client.get(f"{short_code}:last_redirect")

                query = select(TShortUrl).where(
                    TShortUrl.short_name == short_code)
                result = await session.execute(query)
                short_url = result.scalars().first()

                if short_url is not None:
                    short_url.redirect_count += redirect_count
                    if last_redirect is not None:
                        short_url.last_redirect = datetime.fromisoformat(
                            last_redirect)
                    await session.commit()
                    # Удалю счетчик из Redis
                    await redis_client.delete(key)

        await asyncio.sleep(300)
