from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from fastapi import FastAPI
from database import init_models
from links.router import router as lrouter
from events.router import router as erouter
from task import delete_expired_links, delete_old_links
from users import fastapi_users, auth_backend, UserCreate, UserRead


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_models()
    task_exp = asyncio.create_task(delete_expired_links())
    task_old = asyncio.create_task(delete_old_links())
    yield
    task_exp.cancel()
    task_old.cancel()

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

app.include_router(lrouter)
app.include_router(erouter)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
