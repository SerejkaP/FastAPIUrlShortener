from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from fastapi import FastAPI
from database import init_models
from links.router import router as links_router
from events.router import router as events_router
from redis_client import close_redis, init_redis
from task import delete_expired_links, delete_old_links, sync_clicks_to_db
from users import fastapi_users, auth_backend, UserCreate, UserRead


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Применение миграции
    await init_models()
    # Старт redis
    await init_redis()
    # Таски для обновления данных в БД
    task_exp = asyncio.create_task(delete_expired_links())
    task_old = asyncio.create_task(delete_old_links())
    task_counter = asyncio.create_task(sync_clicks_to_db())
    yield
    task_counter.cancel()
    task_exp.cancel()
    task_old.cancel()
    await close_redis()

app = FastAPI(
    lifespan=lifespan
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(links_router)
app.include_router(events_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
