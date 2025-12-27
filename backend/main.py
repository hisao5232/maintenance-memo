from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional, Any
from pydantic import BaseModel

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

# --- Pydanticモデル定義 ---

class RecordBase(BaseModel):
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

# --- APIエンドポイント ---

# 1. メモの登録
@app.post("/records/", response_model=RecordResponse)
def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    # .dict() は Pydantic v2 では .model_dump() 推奨ですが、互換性のため一旦そのままでもOK
    db_record = models.MaintenanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 2. メモの一覧取得（AND検索（絞り込み検索）
@app.get("/records/", response_model=List[RecordResponse])
def read_records(
    q: Optional[str] = None, 
    category: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.MaintenanceRecord)
    
    if category:
        query = query.filter(models.MaintenanceRecord.category == category)
    
    if q:
        # 全角・半角スペースの両方で分割できるようにする
        keywords = q.replace('　', ' ').split()
        
        for kw in keywords:
            search = f"%{kw}%"
            # 各単語に対して「型式」「機番」「内容」のいずれかに含まれるかチェック
            query = query.filter(
                (models.MaintenanceRecord.model_name.ilike(search)) |
                (models.MaintenanceRecord.serial_number.ilike(search)) |
                (models.MaintenanceRecord.content.ilike(search))
            )
    
    # 最後に日付の新しい順に並べ替えると見やすいです
    return query.order_by(models.MaintenanceRecord.date.desc()).all()

# 3. 削除機能 (クラス名を MaintenanceRecord に修正)
@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    # 修正ポイント: database.get_db ではなく get_db を使用
    # 修正ポイント: models.Record ではなく models.MaintenanceRecord を使用
    db_record = db.query(models.MaintenanceRecord).filter(models.MaintenanceRecord.id == record_id).first()
    
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(db_record)
    db.commit()
    return {"message": "削除に成功しました"}
    