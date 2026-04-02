"""
数据库初始化脚本 - 添加预设数据
"""
import sys
sys.path.append('.')

from storage.database import SessionLocal, Source, Item
from services.rss_fetcher import RECOMMENDED_RSS_FEEDS, ENGLISH_RSS_FEEDS
from services.news_fetcher import HOT_TOPICS
from services.newsletter_fetcher import RECOMMENDED_NEWSLETTERS


def init_sources():
    """初始化信息源"""
    db = SessionLocal()
    try:
        # 添加推荐 RSS 源（中文）
        for feed in RECOMMENDED_RSS_FEEDS:
            existing = db.query(Source).filter(
                Source.url == feed["url"]
            ).first()
            if not existing:
                source = Source(
                    type="rss",
                    name=feed["name"],
                    url=feed["url"],
                    category=feed["category"],
                    is_active=True,
                )
                db.add(source)
                print(f"Added RSS source: {feed['name']}")

        # 添加英文 RSS 源（会自动翻译）
        for feed in ENGLISH_RSS_FEEDS:
            existing = db.query(Source).filter(
                Source.url == feed["url"]
            ).first()
            if not existing:
                source = Source(
                    type="rss",
                    name=feed["name"],
                    url=feed["url"],
                    category=feed["category"],
                    is_active=True,
                    is_english=True,  # 标记为英文源
                )
                db.add(source)
                print(f"Added English RSS source: {feed['name']}")

        # 添加新闻话题
        for topic in HOT_TOPICS:
            existing = db.query(Source).filter(
                Source.type == "news",
                Source.url == topic
            ).first()
            if not existing:
                source = Source(
                    type="news",
                    name=f"新闻：{topic}",
                    url=topic,  # 用关键词作为 URL
                    category="新闻",
                    is_active=True,
                )
                db.add(source)
                print(f"Added news topic: {topic}")

        # 添加推荐 Newsletter
        for nl in RECOMMENDED_NEWSLETTERS:
            existing = db.query(Source).filter(
                Source.url == nl.get("url", "")
            ).first()
            if not existing:
                source = Source(
                    type="newsletter",
                    name=nl["name"],
                    url=nl.get("url", ""),
                    category=nl.get("category", "general"),
                    is_active=True,
                )
                db.add(source)
                print(f"Added newsletter: {nl['name']}")

        db.commit()
        print("\n初始化完成!")

    except Exception as e:
        db.rollback()
        print(f"初始化失败：{e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_sources()
