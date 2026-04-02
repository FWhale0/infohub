from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Literal, Optional
from sqlalchemy.orm import Session
from storage.database import get_db, Source
from datetime import datetime

router = APIRouter(prefix="/api/sources", tags=["sources"])


class SourceCreate(BaseModel):
    type: Literal["rss", "news", "newsletter"]
    name: str
    url: str
    category: str = "general"


class SourceResponse(SourceCreate):
    id: int
    is_active: bool = True
    created_at: datetime
    last_fetch: Optional[datetime] = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[SourceResponse])
async def list_sources(db: Session = Depends(get_db)):
    """获取所有信息源"""
    sources = db.query(Source).all()
    return sources


@router.post("/", response_model=SourceResponse)
async def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """添加新信息源"""
    db_source = Source(
        type=source.type,
        name=source.name,
        url=source.url,
        category=source.category,
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    """删除信息源"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(source)
    db.commit()
    return {"message": f"Source {source_id} deleted"}


@router.put("/{source_id}/toggle")
async def toggle_source(source_id: int, db: Session = Depends(get_db)):
    """切换信息源状态"""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.is_active = not source.is_active
    db.commit()
    return {"is_active": source.is_active}
