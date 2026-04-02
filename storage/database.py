"""数据库模型和操作"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import get_settings

settings = get_settings()

# 确保数据目录存在
import os
os.makedirs("./data", exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Source(Base):
    """信息源表"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20))  # rss, news, newsletter
    name = Column(String(255))
    url = Column(String(1000))
    category = Column(String(100), default="general")
    is_active = Column(Boolean, default=True)
    is_english = Column(Boolean, default=False)  # 是否是英文源（会自动翻译）
    created_at = Column(DateTime, default=datetime.now)
    last_fetch = Column(DateTime, nullable=True)


class Item(Base):
    """采集的内容项"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    url = Column(String(1000), unique=True)
    source_id = Column(Integer, nullable=True)
    source_type = Column(String(20))  # rss, news, newsletter
    source_name = Column(String(255))

    # 内容
    raw_content = Column(Text)
    summary = Column(Text, nullable=True)

    # AI 处理结果
    quality_score = Column(Float, default=0.0)
    originality_score = Column(Float, default=0.0)
    depth_score = Column(Float, default=0.0)
    credibility_score = Column(Float, default=0.0)
    category = Column(String(100), default="general")

    # 状态
    is_processed = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    user_rating = Column(Integer, nullable=True)

    # 事件聚类
    cluster_id = Column(String(100), nullable=True)

    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


class Event(Base):
    """事件表（聚类后的）"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500))
    cluster_id = Column(String(100), unique=True)
    timeline = Column(Text)  # JSON
    key_facts = Column(Text)  # JSON
    item_count = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now)


# 创建表
Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
