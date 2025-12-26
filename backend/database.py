import os
from sqlalchemy import create_engine  # create_all を削除
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 環境変数 DATABASE_URL を取得する（設定されていなければデフォルト値を使用）
# docker-compose.yml の environment で設定した値がここに入ります
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://hisao_admin:password@db:5432/maintenance_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

