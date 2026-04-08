# import json
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker,declarative_base
# from EthanChat.settings import Settings
# engine = create_engine(
#     Settings.basic_settings.SQLALCHEMY_DATABASE_URI,
#     json_serializer=lambda obj: json.dumps(obj, ensure_ascii = False),
# )

from datetime import datetime, timezone

from sqlalchemy import Column,DateTime,Integer,String

class BaseModel:
    """基础模型"""

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    create_time = Column(DateTime, default=datetime.now(timezone.utc), comment="创建时间")
    update_time = Column(DateTime, default=None, onupdate=datetime.now(timezone.utc),comment="更新时间")
    create_by = Column(String, default=None, comment="创建者")
    update_by = Column(String, default=None, comment="更新者")

