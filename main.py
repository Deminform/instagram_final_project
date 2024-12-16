import re
from contextlib import asynccontextmanager
from typing import Callable, Dict

from pathlib import Path

from redis import asyncio as aioredis
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from conf import messages
from conf.config import app_config
from src.services import healthchecker
from src.users.routes import router as users_router


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    redis = aioredis.from_url(app_config.REDIS_URL, encoding='utf8')
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    await FastAPILimiter.init(redis)

    yield

    await redis.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(healthchecker.router, prefix="/api")
app.include_router(users_router, prefix="/users", tags=["users"])