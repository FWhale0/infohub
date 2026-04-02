"""
InfoHub - AI 驱动的信息聚合应用
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from config import get_settings
from storage.database import Base, engine
from services.scheduler import scheduler

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("Starting InfoHub...")

    # 创建数据库表
    Base.metadata.create_all(bind=engine)

    # 初始化预设数据源
    from scripts.init_db import init_sources
    init_sources()

    # 启动定时任务（可选，调试时可关闭）
    # scheduler.start()

    yield

    # 关闭时
    print("Shutting down InfoHub...")
    try:
        scheduler.stop()
    except:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-driven information aggregator",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# 挂载静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """前端页面入口"""
    return FileResponse(INDEX_FILE)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


# Import routes after app is created to avoid circular imports
from api import sources, items, dashboard  # noqa

# 注册路由
app.include_router(sources.router)
app.include_router(items.router)
app.include_router(dashboard.router)


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    requested = STATIC_DIR / full_path
    if requested.is_file():
        return FileResponse(requested)

    return FileResponse(INDEX_FILE)
