from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from storage.database import get_db, Item, Source
from services.scheduler import default_rss_fetch, default_news_fetch, default_ai_process

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class CategoryStat(BaseModel):
    category: str
    count: int


class DailySummary(BaseModel):
    date: date
    total_items: int
    pending_items: int
    quality_items: int
    top_categories: List[CategoryStat]
    source_distribution: Dict[str, int]


@router.get("/summary", response_model=DailySummary)
async def get_daily_summary(db: Session = Depends(get_db)):
    """获取每日摘要"""
    # 今日收录总数
    today = datetime.now().date()
    total_items = db.query(Item).count()

    # 待处理数量
    pending_items = db.query(Item).filter(Item.is_processed == False).count()

    # 高质量内容 (评分 >= 7)
    quality_items = db.query(Item).filter(Item.quality_score >= 7).count()

    # 分类统计
    category_stats = db.query(
        Item.category, func.count(Item.id)
    ).group_by(Item.category).all()
    top_categories = [{"category": cat, "count": cnt} for cat, cnt in category_stats]

    # 来源类型分布
    source_stats = db.query(
        Item.source_type, func.count(Item.id)
    ).group_by(Item.source_type).all()
    source_distribution = {stype: cnt for stype, cnt in source_stats}

    return DailySummary(
        date=today,
        total_items=total_items,
        pending_items=pending_items,
        quality_items=quality_items,
        top_categories=top_categories,
        source_distribution=source_distribution,
    )


class EventItem(BaseModel):
    id: int
    title: str
    category: str
    quality_score: float
    published_at: datetime


class EventGroup(BaseModel):
    topic: str
    item_count: int
    items: List[EventItem]
    updated_at: datetime


@router.get("/events")
async def get_recent_events(db: Session = Depends(get_db)):
    """获取近期事件脉络（按聚类分组）"""
    # 简单版本：按时间和标题相似度分组
    # 完整版需要使用 AI 聚类

    items = db.query(Item).filter(
        Item.is_processed == True,
        Item.cluster_id != None
    ).order_by(desc(Item.published_at)).limit(50).all()

    # 按 cluster_id 分组
    clusters = {}
    for item in items:
        if item.cluster_id not in clusters:
            clusters[item.cluster_id] = []
        clusters[item.cluster_id].append(EventItem(
            id=item.id,
            title=item.title,
            category=item.category,
            quality_score=item.quality_score,
            published_at=item.published_at,
        ))

    return [
        EventGroup(
            topic=f"事件 {cid[:8]}..." if cid else "未分类",
            item_count=len(itms),
            items=itms,
            updated_at=max(i.published_at for i in itms),
        )
        for cid, itms in clusters.items()
    ]


@router.get("/trends")
async def get_trends(db: Session = Depends(get_db)):
    """获取热门话题趋势"""
    # 按分类统计最近 24 小时的内容数量
    from sqlalchemy import and_

    cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    trends = db.query(
        Item.category, func.count(Item.id)
    ).filter(
        Item.published_at >= cutoff
    ).group_by(Item.category).order_by(
        desc(func.count(Item.id))
    ).limit(10).all()

    return [{"category": cat, "count": cnt} for cat, cnt in trends]


@router.post("/run-fetch")
async def run_fetch_now():
    """手动触发一轮采集（RSS + News）。"""
    await default_rss_fetch()
    await default_news_fetch()
    return {"status": "ok", "message": "采集完成"}


@router.post("/run-process")
async def run_process_now():
    """手动触发一轮 AI 处理。"""
    await default_ai_process()
    return {"status": "ok", "message": "处理完成"}
