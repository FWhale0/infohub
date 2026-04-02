"""任务调度服务"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import List
import asyncio


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """启动调度器"""
        self.scheduler.start()
        print("Task scheduler started")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        print("Task scheduler stopped")

    def add_rss_fetch_job(self, fetch_func, minutes: int = 30):
        """添加 RSS 采集任务"""
        self.scheduler.add_job(
            fetch_func,
            trigger=IntervalTrigger(minutes=minutes),
            id="rss_fetch",
            replace_existing=True,
        )
        print(f"RSS fetch job scheduled every {minutes} minutes")

    def add_news_fetch_job(self, fetch_func, minutes: int = 60):
        """添加新闻采集任务"""
        self.scheduler.add_job(
            fetch_func,
            trigger=IntervalTrigger(minutes=minutes),
            id="news_fetch",
            replace_existing=True,
        )
        print(f"News fetch job scheduled every {minutes} minutes")

    def add_processing_job(self, process_func, minutes: int = 10):
        """添加 AI 处理任务"""
        self.scheduler.add_job(
            process_func,
            trigger=IntervalTrigger(minutes=minutes),
            id="ai_process",
            replace_existing=True,
        )
        print(f"AI processing job scheduled every {minutes} minutes")


# 全局实例
scheduler = TaskScheduler()


# 默认任务函数
async def default_rss_fetch():
    """默认 RSS 采集任务"""
    from storage.database import SessionLocal, Source
    from services.rss_fetcher import fetch_rss_feed
    from services.ai_processor import ai_processor
    from storage.database import Item

    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.type == "rss", Source.is_active == True).all()

        for source in sources:
            print(f"Fetching RSS: {source.name}")
            items = await fetch_rss_feed(source.url)

            for item_data in items:
                # 检查是否已存在
                existing = db.query(Item).filter(Item.url == item_data["url"]).first()
                if existing:
                    # 旧数据通常只有链接或短摘要，重抓时回填正文。
                    new_raw = item_data.get("raw_content", "")
                    if new_raw and (not existing.raw_content or len(existing.raw_content) < 200):
                        existing.raw_content = new_raw
                    continue

                # 保存原始数据
                new_item = Item(
                    title=item_data["title"],
                    url=item_data["url"],
                    source_id=source.id,
                    source_type="rss",
                    source_name=source.name,
                    raw_content=item_data["raw_content"],
                    published_at=item_data["published_at"],
                    is_processed=False,
                )
                db.add(new_item)

            source.last_fetch = datetime.now()
            db.commit()

        print(f"RSS fetch completed, fetched {len(items)} items from {len(sources)} sources")
    finally:
        db.close()


async def default_news_fetch():
    """默认新闻采集任务"""
    from storage.database import SessionLocal
    from services.news_fetcher import fetch_google_news_rss, HOT_TOPICS
    from storage.database import Item

    db = SessionLocal()
    try:
        for topic in HOT_TOPICS[:3]:  # 限制话题数量
            print(f"Fetching news for: {topic}")
            items = await fetch_google_news_rss(topic)

            for item_data in items:
                existing = db.query(Item).filter(Item.url == item_data["url"]).first()
                if existing:
                    continue

                new_item = Item(
                    title=item_data["title"],
                    url=item_data["url"],
                    source_type="news",
                    source_name=item_data["source_title"],
                    raw_content=item_data["raw_content"],
                    published_at=item_data["published_at"],
                    is_processed=False,
                )
                db.add(new_item)

            db.commit()

        print(f"News fetch completed")
    finally:
        db.close()


async def default_ai_process():
    """默认 AI 处理任务"""
    from storage.database import SessionLocal
    from services.ai_processor import ai_processor
    from storage.database import Item

    db = SessionLocal()
    try:
        # 获取未处理的内容
        items = db.query(Item).filter(Item.is_processed == False).limit(10).all()

        for item in items:
            print(f"Processing: {item.title[:50]}...")

            # 生成摘要
            summary = await ai_processor.summarize(item.title, item.raw_content)
            item.summary = summary

            # 质量评分
            quality = await ai_processor.evaluate_quality(item.title, item.raw_content)
            item.quality_score = quality.get("score", 5)
            item.originality_score = quality.get("originality", 5)
            item.depth_score = quality.get("depth", 5)
            item.credibility_score = quality.get("credibility", 5)

            # 分类
            category = await ai_processor.categorize(item.title, item.raw_content)
            item.category = category

            item.is_processed = True
            db.commit()

        print(f"AI processing completed, processed {len(items)} items")
    finally:
        db.close()


# 需要导入的模块
from datetime import datetime