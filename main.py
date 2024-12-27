from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


from fastapi.responses import HTMLResponse
from conf.config import app_config
from src.services import healthchecker
from src.services.auth.routes import router as auth_router
from src.users.routes import router as users_router
from src.users.routes import router_admin as users_router_admin
from src.posts.routes import router as posts_router
from src.posts.routes import router_admin as posts_router_admin
from src.scores.routes import router as scores_router
from src.comments.router import router as comment_router


BASE_DIR = Path(__file__).parent
templates_path = BASE_DIR.joinpath('src', 'templates')
static_files_path = BASE_DIR.joinpath('src', 'static')
templates = Jinja2Templates(directory=templates_path)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    redis = aioredis.from_url(app_config.REDIS_URL, encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    await FastAPILimiter.init(redis)

    yield

    await redis.close()


app = FastAPI(title="Contact Application", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory=static_files_path), name="static")
app.include_router(healthchecker.router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/api")
app.include_router(posts_router_admin, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(users_router_admin, prefix="/api")
app.include_router(scores_router, prefix="/api")
app.include_router(comment_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'page_title': 'STRONG NUTS | Final Project'})
