from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional, Any
from pydantic import BaseModel

# 別で作った設定ファイルをインポート
import models
from database import engine, SessionLocal

# データベースのテーブルを自動生成
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="整備メモ API")

# DBセッションの取得用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- リクエスト/レスポンス用のデータ型定義 (Pydantic) ---

class RecordBase(BaseModel):
    # すべて Optional にし、デフォルトを None に設定
    category: Optional[Any] = None
    date: Optional[Any] = None
    model_name: Optional[Any] = None
    serial_number: Optional[Any] = None
    content: Optional[Any] = None

    class Config:
        from_attributes = True

class RecordCreate(RecordBase):
    pass

class RecordResponse(RecordBase):
    id: int
    class Config:
        from_attributes = True

# --- APIエンドポイント ---

# 1. メモの登録
@app.post("/records/", response_model=RecordResponse)
def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    db_record = models.MaintenanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 2. メモの一覧取得（検索も可能）
@app.get("/records/", response_model=List[RecordResponse])
def read_records(
    q: Optional[str] = None, 
    category: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.MaintenanceRecord)
    
    # カテゴリ絞り込み
    if category:
        query = query.filter(models.MaintenanceRecord.category == category)
    
    # キーワード検索（型式、機番、内容からあいまい検索）
    if q:
        search = f"%{q}%"
        query = query.filter(
            (models.MaintenanceRecord.model_name.ilike(search)) |
            (models.MaintenanceRecord.serial_number.ilike(search)) |
            (models.MaintenanceRecord.content.ilike(search))
        )
    
    return query.all()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

