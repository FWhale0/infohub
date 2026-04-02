from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from storage.database import get_db, Item

router = APIRouter(prefix="/api/items", tags=["items"])


class ItemResponse(BaseModel):
    id: int
    title: str
    url: str
    source_type: str
    source_name: str
    summary: Optional[str] = None
    raw_content: Optional[str] = None
    quality_score: float = 0.0
    category: str = "general"
    published_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ItemResponse])
async def list_items(
    category: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    min_quality: Optional[float] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """获取处理后的信息列表"""
    query = db.query(Item)

    if category:
        query = query.filter(Item.category == category)
    if source_type:
        query = query.filter(Item.source_type == source_type)
    if min_quality:
        query = query.filter(Item.quality_score >= min_quality)

    items = query.order_by(desc(Item.published_at)).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """获取单条详情"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/{item_id}/rate")
async def rate_item(
    item_id: int,
    score: int,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """用户对内容进行评分，用于改进推荐"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.user_rating = score
    db.commit()
    return {"message": "Rating recorded", "item_id": item_id, "score": score}


@router.post("/{item_id}/read")
async def mark_as_read(item_id: int, db: Session = Depends(get_db)):
    """标记为已读"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_read = True
    db.commit()
    return {"message": "Marked as read"}
