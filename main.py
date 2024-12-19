from contextlib import asynccontextmanager

from redis import asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter

from conf.config import app_config
from src.services import healthchecker
from src.services.auth.routes import router as auth_router
from src.users.routes import router as users_router
from src.posts.routes import router as posts_router


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
app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/api")
app.include_router(users_router, prefix="/api")
