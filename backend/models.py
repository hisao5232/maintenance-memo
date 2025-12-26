from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

class MaintenanceRecord(Base):
    """
    整備メモおよびマニュアル情報を保存するテーブル
    """
    __tablename__ = "maintenance_records"

    # プライマリキー（自動で増えるID）
    id = Column(Integer, primary_key=True, index=True)

    # 分類： "manual" (マニュアル系) or "service" (整備系)
    category = Column(String, nullable=True)

    # 日付： 整備日やマニュアル作成日
    date = Column(Date, nullable=True)

    # 型式： 例 PC200-10
    model_name = Column(String, index=True, nullable=True)

    # 機番： シリアルナンバー
    serial_number = Column(String, index=True, nullable=True)

    # 内容： 修理の詳細やメモ
    content = Column(Text, nullable=True)
